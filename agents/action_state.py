from typing import Union
from etc.messages import Message
import etc.gamestate as gs

# Keep the following in short-term memory, for each potency option used.
# STATE VARIABLES
# Number of red opinions [int]
# Number of blue opinions [int]
# Number of red followers [int]
# Blue energy [int - convert from continuous float to discrete]
#
# PARAMETERS IN CALCULATION
# Round number
# Change in red opinion
# Change in blue opinion
# Change in red followers
# Change in blue energy
# Used to update state_action_lut at end of game by the heuristic,
# For blue:
# ((Change in blue opinions) - (Change in red opinions) - (Change in Red followers) - (Change in blue energy)) * (Rounds to win)
# Red has the opposite heuristic
# There, learning. Are ya happy?????


class ActionState:
    BINS = 5

    # STATE (digitized from continuous)
    n_blue_opinion_bin: int
    n_red_opinion_bin: int
    n_red_followers_bin: int
    blue_energy_bin: int

    iteration: int

    # ACTION
    action: Message

    # RESULTING STATE
    change_n_blue_opinion: int
    change_n_red_opinion: int
    change_n_red_followers: int
    change_blue_energy: int

    # Assume value is between 0 and range.
    @staticmethod
    def bin(value: Union[float, int], bins: int, range: Union[float, int]) -> int:
        clamp_value = max(min(value, range), 0)
        return int(clamp_value / (range / (bins - 1)))

    def __init__(self, action: Message, start_state: "gs.GameState", next_state: "gs.GameState") -> None:
        start_n_red_opinion, start_n_blue_opinion = start_state.count_majority()
        next_n_red_opinion, next_n_blue_opinion = next_state.count_majority()
        green_population = start_state.n_green_agents
        max_energy = start_state.blue_agent.initial_energy

        # STATE
        self.n_red_opinion_bin = ActionState.bin(start_n_red_opinion, ActionState.BINS, green_population)
        self.n_blue_opinion_bin = ActionState.bin(start_n_blue_opinion, ActionState.BINS, green_population)
        self.n_red_followers_bin = ActionState.bin(start_state.red_agent.red_followers, ActionState.BINS, green_population)
        self.blue_energy_bin = ActionState.bin(start_state.blue_agent.blue_energy, ActionState.BINS, max_energy)

        # ACTION
        self.iteration = start_state.iteration
        self.action = action
        self.change_n_blue_opinion = next_n_blue_opinion - start_n_blue_opinion
        self.change_n_red_opinion = next_n_red_opinion - start_n_red_opinion
        self.change_n_red_followers = next_state.red_agent.red_followers - start_state.red_agent.red_followers
        self.change_blue_energy = next_state.blue_agent.blue_energy - start_state.blue_agent.blue_energy
        pass

    # Relative to the blue agent - invert for red agent.
    def rate_state_action(self, round_end: int, lost: bool) -> float:
        local_effect = self.change_n_blue_opinion + self.change_n_red_opinion + self.change_blue_energy + self.change_n_red_followers
        return (-1 if lost else 1) * (round_end - self.iteration) * local_effect
