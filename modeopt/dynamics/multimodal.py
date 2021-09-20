#!/usr/bin/env python3
from gpflow.conditionals import uncertain_conditional
from dataclasses import dataclass
from typing import NewType, Callable
from gpflow import default_float

import tensor_annotations.tensorflow as ttf
import tensorflow as tf
from mogpe.mixture_of_experts import MixtureOfSVGPExperts
from tensor_annotations import axes
from tensor_annotations.axes import Batch
from modeopt.dynamics_new import SVGPDynamics


StateDim = NewType("StateDim", axes.Axis)
ControlDim = NewType("ControlDim", axes.Axis)


# @dataclass
# @gin.configurable
# class TransitionModelTrainingSpec:
#     """
#     Specification data class for model training. Models that require additional parameters for
#     training should create a subclass of this class and add additional properties.
#     """

#     epochs: int
#     training_batch_size: int
#     logging_epoch_freq: int


class ModeOptDynamics:
    def __init__(
        self,
        mosvgpe: MixtureOfSVGPExperts,
        desired_mode: int,
        nominal_dynamics: Callable,
        state_dim: int,
        control_dim: int,
        optimizer: tf.optimizers.Optimizer = tf.optimizers.Adam(),
        num_ckpts: int = 5,
        log_dir: str = "./",
    ):
        self.trainable_model = mosvgpe
        self.set_desired_mode(desired_mode)
        self.desired_mode_dynamics = SVGPDynamics(
            self.dynamics_gp, nominal_dynamics=nominal_dynamics
        )

        self.gating_gp = self.trainable_model.gating_network

        self.optimizer = optimizer

        # Init checkpoint manager for saving model during training
        # self.ckpt = tf.train.Checkpoint(model=self.trainable_model)
        # self.manager = tf.train.CheckpointManager(
        #     self.ckpt, log_dir, max_to_keep=num_ckpts
        # )

        # self.monitor = Monitor(fast_tasks, slow_tasks)
        # self.monitor = None

    @property
    def desired_mode(self):
        return self._desied_mode

    def set_desired_mode(self, desired_mode):
        """Set the desired dynamics mode GP"""
        assert desired_mode < self.mosvgpe.num_experts
        self._desied_mode = desired_mode
        dynamics_gp = self.mosvgpe.experts.experts_list[desired_mode]
        self._desired_mode_dynamics = SVGPDynamics(dynamics_gp)

    def _desired_mode_dynamics(
        self,
        state_mean: ttf.Tensor2[Batch, StateDim],
        control_mean: ttf.Tensor2[Batch, ControlDim],
        state_var: ttf.Tensor2[Batch, StateDim] = None,
        control_var: ttf.Tensor2[Batch, ControlDim] = None,
    ):
        return self._desired_mode_dynamics(
            state_mean, control_mean, state_var=state_var, control_var=control_var
        )

    def call(
        self,
        state_mean: ttf.Tensor2[Batch, StateDim],
        control_mean: ttf.Tensor2[Batch, ControlDim],
        state_var: ttf.Tensor2[Batch, StateDim] = None,
        control_var: ttf.Tensor2[Batch, ControlDim] = None,
    ):
        return self._desired_mode_dynamics(
            state_mean, control_mean, state_var=state_var, control_var=control_var
        )

    def mode_variational_expectation(
        self,
        state_mean: ttf.Tensor2[Batch, StateDim],
        control_mean: ttf.Tensor2[Batch, ControlDim],
        state_var: ttf.Tensor2[Batch, StateDim] = None,
        control_var: ttf.Tensor2[Batch, ControlDim] = None,
    ):
        """Calculate expected log mode probability under trajectory distribution given by,

        \sum_{t=1}^T \E_{p(\state_t, \control_t)} [\log \Pr(\alpha=k_* \mid \state_t, \control_t)]

        \sum_{t=1}^T \E_{p(\state_t, \control_t, h)} [\log \Pr(\alpha=k_* \mid h(\state_t, \control_t) )]
        """
        # Calculate expected mode prob
        gating_means, gating_vars = self.uncertain_predict_gating(
            state_mean, control_mean, state_var, control_var
        )
        print("gating_means")
        print(gating_means)
        print(gating_vars)
        Y = tf.ones(gating_means.shape, dtype=default_float()) * self.desired_mode
        gating_var_exp = self.gating_gp.likelihood.variational_expectations(
            gating_means, gating_vars, Y
        )
        print("gating_var_exp")
        print(gating_var_exp)
        sum_gating_var_exp = tf.reduce_sum(gating_var_exp)
        print(sum_gating_var_exp)
        return sum_gating_var_exp

    def uncertain_predict_gating(
        self,
        state_mean: ttf.Tensor2[Batch, StateDim],
        control_mean: ttf.Tensor2[Batch, ControlDim],
        state_var: ttf.Tensor2[Batch, StateDim] = None,
        control_var: ttf.Tensor2[Batch, ControlDim] = None,
    ):
        input_mean = tf.concat([state_mean, control_mean], -1)
        if state_var is None or control_var is None:
            h_mean, h_var = self.gating_gp.predict_f(input_mean, full_cov=False)
        else:
            input_var = tf.concat([state_var, control_var], -1)
            h_mean, h_var = uncertain_conditional(
                input_mean,
                input_var,
                # state_var,
                self.gating_gp.inducing_variable,
                kernel=self.gating_gp.kernel,
                q_mu=self.gating_gp.q_mu,
                q_sqrt=self.gating_gp.q_sqrt,
                mean_function=self.gating_gp.mean_function,
                full_output_cov=False,
                full_cov=False,
                white=self.gating_gp.whiten,
            )
        return h_mean, h_var

    # def _build_training_loss(
    #     self,
    #     latent_trajectories: Trajectory,
    #     training_spec: TransitionModelTrainingSpec,
    # ) -> Callable:
    #     transition = extract_transitions_from_trajectories(
    #         latent_trajectories,
    #         self.latent_observation_space_spec,
    #         self.action_space_spec,
    #         self.predict_state_difference,
    #     )

    #     train_dataset = transitions_to_tf_dataset(
    #         transition, predict_state_difference=self.predict_state_difference
    #     )
    #     num_train_data = train_dataset[0].shape[0]

    #     prefetch_size = tf.data.experimental.AUTOTUNE
    #     shuffle_buffer_size = num_train_data // 2
    #     num_batches_per_epoch = num_train_data // training_spec.training_batch_size

    #     train_dataset = (
    #         train_dataset.repeat()
    #         .prefetch(prefetch_size)
    #         .shuffle(buffer_size=shuffle_buffer_size)
    #         .batch(training_spec.training_batch_size)
    #     )

    #     print(f"prefetch_size={prefetch_size}")
    #     print(f"shuffle_buffer_size={shuffle_buffer_size}")
    #     print(f"num_batches_per_epoch={num_batches_per_epoch}")

    #     training_loss = self._model.training_loss_closure(iter(train_dataset))
    #     return training_loss, num_batches_per_epoch

    # def _train(
    #     self,
    #     latent_trajectories: Trajectory,
    #     training_spec: TransitionModelTrainingSpec,
    # ):
    #     """Train the transition_model given the trajectories and a training_spec

    #     :param latent_trajectories: Trajectories of latent states, actions, rewards and next latent
    #         states.
    #     :param training_spec: training specifications with `batch_size`, `epochs`, `callbacks` etc.
    #     """

    #     training_loss, num_batches_per_epoch = self._build_training_loss(
    #         latent_trajectories, training_spec
    #     )

    #     @tf.function
    #     def tf_optimization_step():
    #         return self.optimizer.minimize(
    #             training_loss, self._model.trainable_variables
    #         )

    #     for epoch in range(training_spec.num_epochs):
    #         for _ in range(num_batches_per_epoch):
    #             tf_optimization_step()
    #         if self.monitor is not None:
    #             self.monitor(epoch)
    #         epoch_id = epoch + 1
    #         if epoch_id % training_spec.logging_epoch_freq == 0:
    #             tf.print(f"Epoch {epoch_id}: ELBO (train) {training_loss()}")
    #             if self.manager is not None:
    #                 self.manager.save()