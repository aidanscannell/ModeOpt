#!/usr/bin/env python3
import typing
import numpy as np
from typing import Callable

import tensor_annotations.tensorflow as ttf
import tensorflow as tf
from gpflow import default_float
from tensor_annotations import axes
from tensor_annotations.axes import Batch
from modeopt.policies import VariationalPolicy

StateDim = typing.NewType("StateDim", axes.Axis)
ControlDim = typing.NewType("ControlDim", axes.Axis)


def rollout_controls_in_dynamics(
    dynamics: Callable,
    start_state: ttf.Tensor2[Batch, StateDim],
    control_means: ttf.Tensor2[Batch, ControlDim],
    start_state_var: ttf.Tensor2[Batch, StateDim] = None,
    control_vars: ttf.Tensor2[Batch, ControlDim] = None,
):
    """Rollout a given set of control means and vars

    :returns: (states_means, state_vars)
    """
    horizon = control_means.shape[0]
    if start_state_var is None:
        start_state_var = tf.zeros((1, start_state.shape[1]), dtype=default_float())

    state_means = start_state
    state_vars = start_state_var
    for t in range(horizon):
        control_mean = control_means[t : t + 1, :]
        if control_vars is not None:
            control_var = control_vars[t : t + 1, :]
        else:
            control_var = None
        next_state_mean, next_state_var = dynamics(
            state_means[-1:, :], control_mean, state_vars[-1:, :], control_var
        )
        state_means = tf.concat([state_means, next_state_mean], 0)
        state_vars = tf.concat([state_vars, next_state_var], 0)
    return state_means, state_vars


def rollout_policy_in_dynamics(
    policy: VariationalPolicy,
    dynamics: Callable,
    start_state: ttf.Tensor2[Batch, StateDim],
    start_state_var: ttf.Tensor2[Batch, StateDim] = None,
):
    """Rollout a polciy in gp dynamics model

    :returns: (states_means, state_vars)
    """
    if start_state_var is None:
        start_state_var = tf.zeros((1, start_state.shape[1]), dtype=default_float())

    state_means = start_state
    state_vars = start_state_var
    for t in range(policy.num_time_steps):
        control_mean, control_var = policy(t)
        next_state_mean, next_state_var = dynamics(
            state_means[-1:, :], control_mean, state_vars[-1:, :], control_var
        )
        state_means = tf.concat([state_means, next_state_mean], 0)
        state_vars = tf.concat([state_vars, next_state_var], 0)
    return state_means, state_vars


def rollout_controller_in_env(
    env, controller, start_state: ttf.Tensor2[Batch, StateDim] = None
):
    """Rollout a controller in an environment"""
    return rollout_policy_in_env(env, controller.policy, start_state)


def rollout_policy_in_env(
    env, policy, start_state: ttf.Tensor2[Batch, StateDim] = None
):
    """Rollout a given policy on an environment

    :param policy: Callable representing policy to rollout
    :param timesteps: number of timesteps to rollout
    :returns: (states, delta_states)
    """
    env.state_init = start_state.numpy()
    env.reset()
    states = start_state.numpy()

    for t in range(policy.num_time_steps):
        control, _ = policy(t)
        next_time_step = env.step(control.numpy())
        states = np.concatenate([states, next_time_step.observation])
    return np.stack(states)
