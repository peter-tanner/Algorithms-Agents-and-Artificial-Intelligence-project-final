from abc import ABC, abstractmethod
import pickle
import shelve
from typing import Dict, List, Tuple, Union

import etc.gamestate as gs
from etc.messages import MESSAGE_UNDEFINED, Message
from etc.util import NoCopyShelf, RecursiveDict
from agents.action_state import ActionState


class AbstractInfluencerAgent(ABC):
    last_message: Message

    # Number of red opinions [int]
    # Number of blue opinions [int]
    # Number of red followers [int]
    # Blue energy [int - convert from continuous float to discrete]
    state_action_lut: Dict[int, Dict[int, Dict[int, Dict[int, Dict[int, List[Union[int, float]]]]]]]
    __state_action_lut: NoCopyShelf

    short_term_mem: List[ActionState]

    def __init__(self, state_action_lut_path: str) -> None:
        self.last_message = MESSAGE_UNDEFINED
        self.__state_action_lut = NoCopyShelf.open(
            state_action_lut_path,
            protocol=pickle.HIGHEST_PROTOCOL,
            writeback=True  # Yes this makes it less performant, but it will be more readable.
        )
        # Create data for new shelve
        try:
            self.__state_action_lut["data"]
        except KeyError:
            self.__state_action_lut["data"] = RecursiveDict()
        self.state_action_lut = self.__state_action_lut["data"]

        self.short_term_mem = []

    @abstractmethod
    def influence(self, state: "gs.GameState", *args, **kwargs) -> None:
        pass

    @abstractmethod
    def smart_influence(self, state: "gs.GameState") -> None:
        pass

    @abstractmethod
    def choices() -> List[Tuple]:
        pass

    @abstractmethod
    def update_short_term_mem(self, old_state: "gs.GameState", resulting_state: "gs.GameState") -> None:
        pass

    @abstractmethod
    def update_lut(self) -> None:
        pass

    def __update_lut_rating__(self, action_state: ActionState, rating: float) -> None:
        # Number of red opinions [int]
        # Number of blue opinions [int]
        # Number of red followers [int]
        # Blue energy [int - convert from continuous float to discrete]
        # Action
        previous_state_ratings: List[int, float] = self.state_action_lut[action_state.n_red_opinion_bin][action_state.n_blue_opinion_bin][
            action_state.n_red_followers_bin][action_state.blue_energy_bin]
        action = action_state.action.id
        if (type(previous_state_ratings[action]) != list):
            previous_state_ratings[action] = [0, 0.0]
        previous_state_ratings[action][0] += 1
        previous_state_ratings[action][1] += rating

    def close_lut(self) -> None:
        self.__state_action_lut.close()

    def sync_lut(self) -> None:
        self.__state_action_lut.sync()
