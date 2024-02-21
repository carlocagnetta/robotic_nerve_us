from gymnasium import Env
import numpy as np
import SimpleITK as sitk


class LabelmapsNavigationEnv(Env):
    def __init__(self, volume: sitk.Image):
        self.volume = volume

    def step(self, action: int):
        pass