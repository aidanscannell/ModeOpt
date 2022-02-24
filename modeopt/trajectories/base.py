#!/usr/bin/env python3
from typing import Optional, Union
import abc

import tensorflow as tf
from modeopt.custom_types import ControlTrajectory, ControlTrajectoryMean


class BaseTrajectory(tf.keras.layers.Layer, abc.ABC):
    def __call__(
        self, timestep: Optional[int] = None, variance: Optional[bool] = False
    ) -> Union[ControlTrajectory, ControlTrajectoryMean]:
        if variance:
            return self.controls, None
        else:
            return self.controls

    def call(self, input) -> ControlTrajectory:
        return self.controls

    @property
    def controls(self) -> ControlTrajectoryMean:
        raise NotImplementedError

    @property
    def horizon(self) -> int:
        return self.controls.shape[0]

    @property
    def control_dim(self) -> int:
        return self.controls.shape[1]

    @abc.abstractmethod
    def copy(self):
        raise NotImplementedError
