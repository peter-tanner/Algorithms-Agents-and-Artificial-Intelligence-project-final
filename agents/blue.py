
import math
from random import Random
import statistics
from typing import List, Tuple
import etc.gamestate as gs
from agents.green import GreenAgent
from agents.gray import GrayAgent
from etc.messages import BLUE_MESSAGES, MESSAGE_BLUE_SPY, MESSAGE_UNDEFINED, Message, Opinion
from agents.abstract_influencer_agent import AbstractInfluencerAgent
from etc.util import RecursiveDict
from agents.action_state import ActionState
from play_config import BLUE_AGENT_LUT_PATH


class BlueAgent(AbstractInfluencerAgent):
    # Energy level for blue team
    blue_energy: float
    initial_energy: float
    blue_count: int
    rand: Random

    # Learn from gray agents
    gray_mem: List[Opinion]

    # Number of red opinions [int]
    # Number of blue opinions [int]
    # Number of red followers [int]
    # Blue energy [int - convert from continuous float to discrete]
    # Action

    def __init__(self, initial_energy: float, rand: Random) -> None:
        super().__init__(BLUE_AGENT_LUT_PATH)
        self.blue_energy = initial_energy
        self.initial_energy = initial_energy
        self.blue_count = 0
        self.rand = rand

        self.gray_mem = [Opinion.BLUE, Opinion.RED]  # Assume 0.5 probability of spy initially.

    # > For a blue agent, the options will consist of a) - 10 correction messages (Please
    # > come up with some fictitious messages), uncertainty value and associated energy loss
    #
    # > blue team can push a counter-narrative and interact with green team members.
    # > However, if they invest too much by interacting with a high certainty,
    #
    # > blue team is changing the opinion of the green team members
    # Interpreting this as blue team being able to affect the uncertainty of green
    # nodes, NOT interacting implying being able to directly switch them to blue
    # by calling person.attempt_switch(Opinion.BLUE)
    # It is stated that blue can "interact with green team members", so I am
    # interpreting this as interacting/influencing ALL green members to vote, not
    # just those with a certain opinion. TO compensate the potency of blue
    # Messages will be halved.

    @staticmethod
    def blue_action(person: GreenAgent, message: Message) -> None:
        if person.polarity == Opinion.RED:
            person.uncertainty += message.potency

    # > the blue team is changing the opinion of the green team members. Blue team
    # > also has an option to let a grey agent in the green network. That agent
    # > can be thought of as a life line, where blue team gets another chance of
    # > interaction without losing “energy”. However, the grey agent can be a
    # > spy from the red team
    # So blue team can directly attempt to make people's opinions switch at the
    # cost of fuel (Unlike red team, which can only decrease red people's certainty
    # but not directly cause people to switch to red team), or use a spy.

    def influence(self, gs: "gs.GameState", message: Message) -> None:
        self.last_message = message
        if message == MESSAGE_BLUE_SPY:
            gray: GrayAgent = self.rand.choice(gs.gray_agents)
            gray.gray_action(gs)

            # Remember the action
            self.gray_mem.append(gray.polarity)
        else:
            for person in gs.green_agents.nodes(data=False):
                self.blue_energy -= message.cost
                obj_person: GreenAgent = gs.get_green_agent(person)
                BlueAgent.blue_action(obj_person, message)

    def choices() -> List[Tuple]:
        choices = [x for x in BLUE_MESSAGES]
        choices.append(MESSAGE_BLUE_SPY)
        return choices

    def gray_mean(self) -> float:
        return statistics.mean([1 if x == Opinion.BLUE else 0 for x in self.gray_mem])

    def choose_gray(self) -> bool:
        return self.rand.uniform(0.0, 1.0) < self.gray_mean()

    # Random process - used to balance the game
    def dumb_influence(self, state: "gs.GameState") -> None:
        self.influence(state, state.rand.choice(BlueAgent.choices()))

    def smart_influence(self, state: "gs.GameState") -> None:
        if self.choose_gray():
            self.influence(state, MESSAGE_BLUE_SPY)
            return

        red_opinion, blue_opinion = state.count_majority()
        n_red_opinion_bin = ActionState.bin(red_opinion, ActionState.BINS, state.n_green_agents)
        n_blue_opinion_bin = ActionState.bin(blue_opinion, ActionState.BINS, state.n_green_agents)
        n_red_followers_bin = ActionState.bin(state.red_agent.red_followers, ActionState.BINS, state.n_green_agents)
        blue_energy_bin = ActionState.bin(state.blue_agent.blue_energy, ActionState.BINS, state.blue_agent.initial_energy)

        previous_rating: RecursiveDict[List[int, float]] = self.state_action_lut[n_red_opinion_bin][n_blue_opinion_bin][
            n_red_followers_bin][blue_energy_bin]

        n_samples = 1
        largest_rating = -math.inf
        largest_action = -1
        for option in previous_rating:
            option_rating_fractional = previous_rating[option]
            rating = option_rating_fractional[1] / option_rating_fractional[0]  # Average
            if rating > largest_rating:
                largest_rating = rating
                largest_action = option
            n_samples += option_rating_fractional[0]

        message: Message
        # Use 1/sqrt(x)
        if self.rand.uniform(0.0, 1.0) < 1 / math.sqrt(n_samples):
            message = state.rand.choice(BLUE_MESSAGES)
        else:
            message = BLUE_MESSAGES[largest_action]
        self.influence(state, message)

    def update_lut(self, terminal_state: "gs.GameState") -> None:
        blue_winner = terminal_state.winner == gs.Winner.BLUE_WIN or terminal_state.winner == gs.Winner.RED_NO_FOLLOWERS
        for action_state in self.short_term_mem:
            rating = action_state.rate_state_action(terminal_state.iteration, blue_winner)
            self.__update_lut_rating__(action_state, rating)

    def update_short_term_mem(self, start_state: "gs.GameState", next_state: "gs.GameState") -> None:
        if self.last_message != MESSAGE_BLUE_SPY:
            self.short_term_mem.append(ActionState(self.last_message, start_state, next_state))
