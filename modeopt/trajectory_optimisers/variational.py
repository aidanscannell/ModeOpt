#!/usr/bin/env python3
import typing
from dataclasses import dataclass
from typing import Callable

import gpflow as gpf
import tensor_annotations.tensorflow as ttf
import tensorflow as tf
from modeopt.dynamics import GPDynamics
from modeopt.cost_functions import expected_quadratic_costs
from modeopt.policies import (
    VariationalPolicy,
    VariationalGaussianPolicy,
    DeterministicPolicy,
)
from modeopt.rollouts import rollout_policy_in_dynamics
from modeopt.trajectory_optimisers.base import TrajectoryOptimiser
from tensor_annotations import axes
from tensor_annotations.axes import Batch

StateDim = typing.NewType("StateDim", axes.Axis)
ControlDim = typing.NewType("ControlDim", axes.Axis)


@dataclass
class VariationalTrajectoryOptimiserTrainingSpec:
    """
    Specification data class for model training. Models that require additional parameters for
    training should create a subclass of this class and add additional properties.
    """

    max_iterations: int = 100
    method: str = "SLSQP"
    disp: bool = True
    monitor: gpf.monitor.Monitor = None
    manager: tf.train.CheckpointManager = None


@dataclass
class ModeVariationalTrajectoryOptimiserTrainingSpec:
    """
    Specification data class for model training. Models that require additional parameters for
    training should create a subclass of this class and add additional properties.
    """

    max_iterations: int = 100
    method: str = "SLSQP"
    disp: bool = True
    mode_chance_constraint_lower: float = None  # lower bound on mode probability over traj, set as None to turn off mode constraints
    compile_mode_constraint_fn: bool = True  # constraints fn in tf.function?
    compile_loss_fn: bool = True  # loss function in tf.function?
    monitor: gpf.monitor.Monitor = None
    manager: tf.train.CheckpointManager = None


class VariationalTrajectoryOptimiser(TrajectoryOptimiser):
    """
    A trajectory optimiser optimises a sequence of actions given a model of the
    the environment that is used for virtual rollouts.
    """

    def __init__(
        self,
        policy: VariationalPolicy,
        dynamics: GPDynamics,
        cost_fn: Callable,
        terminal_cost_fn: Callable,
    ):
        super().__init__(
            policy=policy,
            dynamics=dynamics,
            cost_fn=cost_fn,
            terminal_cost_fn=terminal_cost_fn,
        )
        self.optimiser = gpf.optimizers.Scipy()

    def build_training_loss(
        self,
        start_state: ttf.Tensor2[Batch, StateDim],
        start_state_var: ttf.Tensor2[Batch, StateDim] = None,
        compile: bool = True,
    ):
        def training_loss():
            return -self.elbo(start_state, start_state_var=start_state_var)

        if compile:
            return tf.function(training_loss)
        else:
            return training_loss

    def optimise(
        self,
        start_state: ttf.Tensor2[Batch, StateDim],
        training_spec: VariationalTrajectoryOptimiserTrainingSpec,
        constraints=[],
    ):
        """Optimise trajectories starting from an initial state"""
        gpf.set_trainable(self.dynamics, False)
        if training_spec.monitor and training_spec.manager:

            def callback(step, variables, values):
                training_spec.monitor(step)
                training_spec.manager.save()
                print("values")
                print(values)
                print("variables")
                print(variables)

        elif training_spec.monitor is not None:

            def callback(step, variables, values):
                training_spec.monitor(step)

        elif training_spec.manager is not None:

            def callback(step, variables, values):
                training_spec.manager.save()

        else:
            callback = None

        training_loss = self.build_training_loss(
            start_state, start_state_var=None, compile=training_spec.compile_loss_fn
        )

        print("self.policy.trainable_variables")
        print(self.policy.trainable_variables)
        optimisation_result = self.optimiser.minimize(
            training_loss,
            self.policy.trainable_variables,
            method=training_spec.method,
            constraints=constraints,
            step_callback=callback,
            options={
                "disp": training_spec.disp,
                "maxiter": training_spec.max_iterations,
            },
        )
        print("Optimisation result:")
        print(optimisation_result)
        print("self.policy.trainable_variables")
        print(self.policy.trainable_variables)
        print("self.policy()")
        print(self.policy())
        print("self.policy.variational_dist.mean()")
        print(self.policy.variational_dist.mean())
        print(self.policy.variational_dist.variance())
        # TODO remember what's trainable in dynamics and make it trainable here
        return optimisation_result

    def elbo(
        self,
        start_state: ttf.Tensor2[Batch, StateDim],
        start_state_var: ttf.Tensor2[Batch, StateDim] = None,
    ):
        """Evidence LOwer Bound"""
        entropy = self.policy.entropy()  # calculate entropy of policy dist

        state_means, state_vars = rollout_policy_in_dynamics(
            self.policy, self.dynamics, start_state, start_state_var=start_state_var
        )

        expected_integral_costs, expected_terminal_cost = expected_costs(
            cost_fn=self.cost_fn,
            terminal_cost_fn=self.terminal_cost_fn,
            state_means=state_means,
            state_vars=state_vars,
            policy=self.policy,
        )

        elbo = (
            -expected_terminal_cost - tf.reduce_sum(expected_integral_costs) - entropy
        )
        return elbo


class ModeVariationalTrajectoryOptimiser(VariationalTrajectoryOptimiser):
    """
    Trajectory optimiser that optimises a policy using variational inference.
    The evidence lower bound includes a conditioning on a mode indicator
    variable, resulting trajectories that attempt to remain in a desired mode.
    """

    def __init__(
        self,
        policy: VariationalPolicy,
        dynamics: GPDynamics,
        cost_fn: Callable,
        terminal_cost_fn: Callable,
    ):
        super().__init__(
            policy=policy,
            dynamics=dynamics,
            cost_fn=cost_fn,
            terminal_cost_fn=terminal_cost_fn,
        )

    def elbo(
        self,
        start_state: ttf.Tensor2[Batch, StateDim],
        start_state_var: ttf.Tensor2[Batch, StateDim] = None,
    ):
        """Optimise trajectories starting from an initial state"""
        entropy = self.policy.entropy()  # calculate entropy of policy dist

        # Rollout controls in dynamics
        state_means, state_vars = rollout_policy_in_dynamics(
            self.policy,
            self.dynamics,
            start_state,
            start_state_var=start_state_var,
        )

        # Calculate costs
        expected_integral_costs, expected_terminal_cost = expected_quadratic_costs(
            cost_fn=self.cost_fn,
            terminal_cost_fn=self.terminal_cost_fn,
            state_means=state_means,
            state_vars=state_vars,
            policy=self.policy,
        )  # [Batch,], []

        control_means, control_vars = self.policy()
        mode_var_exp = self.dynamics.mode_variational_expectation(
            state_means[:-1, :], control_means, state_vars[:-1, :], control_vars
        )

        elbo = (
            -mode_var_exp
            - expected_terminal_cost
            - tf.reduce_sum(expected_integral_costs)
            + entropy
        )
        print("elbo")
        print(elbo)
        print("mode_var_exp")
        print(mode_var_exp)
        print("expected_terminal_cost")
        print(expected_terminal_cost)
        print("expected_integral_cost")
        print(expected_integral_costs)
        # print("entropy")
        # print(entropy)
        return elbo