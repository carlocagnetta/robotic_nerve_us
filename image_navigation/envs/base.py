from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import gymnasium as gym
import numpy as np
from gymnasium.core import ActType as TAction, ObsType as TObs


class EnvPreconditionError(RuntimeError):
    pass


@dataclass(kw_only=True)
class StateAction:
    action: Any
    # state of the env will be reflected by fields added to subclasses
    # but action is a reserved field name. Subclasses should override the
    # type of action to be more specific


TStateAction = TypeVar("TStateAction", bound=StateAction)
TEnv = TypeVar("TEnv", bound="ModularEnv")


class RewardMetric(Generic[TStateAction], ABC):
    @abstractmethod
    def compute_reward(self, state: TStateAction) -> float:
        pass

    @property
    @abstractmethod
    def range(self) -> tuple[float, float]:
        pass


class TerminationCriterion(Generic[TEnv], ABC):
    @abstractmethod
    def should_terminate(self, env: TEnv) -> bool:
        pass


class NeverTerminate(TerminationCriterion[TStateAction]):
    def should_terminate(self, env: TEnv) -> bool:
        return False


class Observation(Generic[TStateAction, TObs], ABC):
    @abstractmethod
    def compute_observation(self, state: TStateAction) -> TObs:
        pass

    @property
    @abstractmethod
    def observation_space(self) -> gym.spaces.Space[TObs]:
        pass


class ArrayObservation(Observation[TStateAction, np.ndarray], Generic[TStateAction], ABC):
    pass


class ModularEnv(gym.Env, Generic[TStateAction, TAction, TObs], ABC):
    def __init__(
        self,
        reward_metric: RewardMetric[TStateAction],
        observation: Observation[TStateAction, TObs],
        termination_criterion: TerminationCriterion | None = None,
        max_episode_len: int | None = None,
    ):
        self.reward_metric = reward_metric
        self.observation = observation
        self.termination_criterion = termination_criterion or NeverTerminate()
        self.max_episode_len = max_episode_len

        self._is_closed = True
        self._is_terminated = False
        self._is_truncated = False
        self._cur_episode_len = 0
        self._cur_observation: TObs | None = None
        self._cur_reward: float | None = None
        self._cur_state_action: TStateAction | None = None


    @dataclass
    class CurEnvStatus:
        episode_len: int
        state_action: TStateAction
        observation: TObs
        reward: float
        is_terminated: bool
        is_truncated: bool
        is_closed: bool
        info: dict[str, Any]


    def get_cur_env_status(self) -> CurEnvStatus:
        return self.CurEnvStatus(
            episode_len=self.cur_episode_len,
            state_action=self.cur_state_action,
            observation=self.cur_observation,
            reward=self.cur_reward,
            is_terminated=self.is_terminated,
            is_truncated=self._is_truncated,
            is_closed=self.is_closed,
            info=self.get_info_dict(),
        )

    @property
    def is_closed(self):
        return self._is_closed

    @property
    def is_terminated(self):
        return self._is_terminated

    @property
    def is_truncated(self):
        return self._is_truncated

    @property
    def cur_state_action(self) -> TStateAction:
        return self._cur_state_action

    @property
    def cur_observation(self) -> TObs:
        return self._cur_observation

    @property
    def cur_reward(self) -> float:
        return self._cur_reward
    @property
    def cur_episode_len(self):
        return self._cur_episode_len


    @property
    @abstractmethod
    def action_space(self) -> gym.spaces.Space[TAction]:  # type: ignore
        pass

    @property
    def observation_space(self) -> gym.spaces.Space[TObs]:  # type: ignore
        return self.observation.observation_space

    def close(self):
        self._cur_state_action = None
        self._is_closed = True
        self._cur_episode_len = 0

    def _assert_cur_state(self):
        if self.cur_state_action is None:
            raise EnvPreconditionError(
                "This operation requires a current state, but none is set. Did you call reset()?"
            )

    @abstractmethod
    def compute_next_state(self, action: TAction) -> TStateAction:
        pass

    @abstractmethod
    def sample_initial_state(self) -> TStateAction:
        pass

    def get_info_dict(self) -> dict:
        # override this if you want to return additional info
        return {}

    def should_terminate(self):
        return self.termination_criterion.should_terminate(self)

    def should_truncate(self):
        if self.max_episode_len is not None:
            return self.cur_episode_len >= self.max_episode_len
        return False

    def compute_cur_observation(self):
        self._assert_cur_state()
        return self.observation.compute_observation(self.cur_state_action)

    def compute_cur_reward(self):
        self._assert_cur_state()
        return self.reward_metric.compute_reward(self.cur_state_action)

    def _update_cur_reward(self):
        self._cur_reward = self.compute_cur_reward()

    def _update_cur_observation(self):
        self._cur_observation = self.compute_cur_observation()

    def _update_is_terminated(self):
        self._is_terminated = self.should_terminate()
        
    def _update_is_truncated(self):
        self._is_truncated = self.should_truncate()

    def _update_observation_reward_termination(self):
        # NOTE: the order of these calls is important!
        self._update_cur_observation()
        self._update_cur_reward()
        self._update_is_terminated()
        self._update_is_truncated()
        
    def _go_to_next_state(self, action: TStateAction):
        self._cur_state_action = self.compute_next_state(action)
        self._update_observation_reward_termination()

    def reset(self, **kwargs):
        super().reset(**kwargs)
        self._cur_state_action = self.sample_initial_state()
        self._is_closed = False
        self._cur_episode_len = 1
        self._update_observation_reward_termination()
        return self.cur_observation, self.get_info_dict()

    def step(self, action: TAction):
        self._go_to_next_state(action)
        self._cur_episode_len += 1
        return self.cur_observation, self.cur_reward, self.is_terminated, self.is_truncated, self.get_info_dict()
