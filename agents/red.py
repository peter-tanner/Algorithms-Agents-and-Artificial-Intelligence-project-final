
# Game Agents
import math
from random import Random
from typing import List, Tuple
from etc.messages import MESSAGE_UNDEFINED, RED_MESSAGES, Message, Opinion
from agents.green import GreenAgent
import etc.gamestate as gs
from agents.abstract_influencer_agent import AbstractInfluencerAgent
from agents.action_state import ActionState
from etc.util import RecursiveDict
from play_config import RED_AGENT_LUT_PATH


class RedAgent(AbstractInfluencerAgent):
    # > A highly potent message may result in losing followers i.e., as compared
    # > to the last round fewer green team members will be able to interact with
    # > the red team agent
    # Assume everyone is a follower at the start
    red_followers: int  # Number of green agents listening to red team
    red_count: int    # Number of green agents with Opinion.RED
    rand: Random

    def __init__(self, initial_followers: int, rand: Random) -> None:
        super().__init__(RED_AGENT_LUT_PATH)
        self.red_followers = initial_followers
        self.red_count = 0
        self.rand = rand

    # > However, a potent message may decrease the uncertainity of opinion among
    # > people who are already under the influence of the red team
    @staticmethod
    def red_action(person: GreenAgent, message: Message):
        if person.following_red and person.polarity == Opinion.RED:
            person.uncertainty -= message.potency

    def influence(self, state: "gs.GameState", message: Message) -> None:
        # No need to deepcopy() since each interaction only affects each person once.
        self.last_message = message
        for person in state.green_agents.nodes(data=False):
            obj_person: GreenAgent = state.get_green_agent(person)
            # > A highly potent message may result in losing followers i.e., as compared
            # > to the last round fewer green team members will be able to interact
            # > with the red team agent
            if self.rand.random() < message.cost:
                if obj_person.following_red:
                    obj_person.unfollow_red()
                    self.red_followers -= 1

            # > However, a potent message may decrease the uncertainity of opinion among
            # > people who are already under the influence of the red team
            else:
                RedAgent.red_action(obj_person, message)

    # Random process
    def dumb_influence(self, state: "gs.GameState") -> None:
        self.influence(state, state.rand.choice(RED_MESSAGES))

    def smart_influence(self, state: "gs.GameState") -> None:
        red_opinion, blue_opinion = state.count_majority()
        n_red_opinion_bin = ActionState.bin(red_opinion, ActionState.BINS, state.n_green_agents)
        n_blue_opinion_bin = ActionState.bin(blue_opinion, ActionState.BINS, state.n_green_agents)
        n_red_followers_bin = ActionState.bin(state.red_agent.red_followers, ActionState.BINS, state.n_green_agents)
        blue_energy_bin = ActionState.bin(state.blue_agent.blue_energy, ActionState.BINS, state.blue_agent.initial_energy)

        previous_rating: RecursiveDict[List[int, float]] = self.state_action_lut[n_red_opinion_bin][n_blue_opinion_bin][
            n_red_followers_bin][blue_energy_bin]

        n_samples = 1
        largest_rating = -math.inf
        largest_action = 0
        for option in previous_rating:
            option_rating_fractional = previous_rating[option]
            rating = option_rating_fractional[1] / option_rating_fractional[0]  # Average
            if rating > largest_rating:
                largest_rating = rating
                largest_action = option
            n_samples += option_rating_fractional[0]

        message: Message
        # Use 1/sqrt(x) - Central-limit theorem
        if self.rand.uniform(0.0, 1.0) < 1 / math.sqrt(n_samples):
            message = state.rand.choice(RED_MESSAGES)
        else:
            message = RED_MESSAGES[largest_action]
        self.influence(state, message)

    def choices() -> List[Tuple]:
        return [(x) for x in RED_MESSAGES]

    def update_short_term_mem(self, start_state: "gs.GameState", next_state: "gs.GameState") -> None:
        self.short_term_mem.append(ActionState(self.last_message, start_state, next_state))

    # ((Change in blue opinions) - (Change in red opinions) - (Change in Red followers) - (Change in blue energy)) * (Rounds to win)
    # Red has the opposite heuristic
    # There, learning. Are ya happy?????
    def update_lut(self, terminal_state: "gs.GameState") -> None:
        blue_winner = terminal_state.winner == gs.Winner.BLUE_WIN or terminal_state.winner == gs.Winner.RED_NO_FOLLOWERS
        for action_state in self.short_term_mem:
            # Since this is the red agent, assign negative to blue wins.
            rating = -action_state.rate_state_action(terminal_state.iteration, blue_winner)
            self.__update_lut_rating__(action_state, rating)
