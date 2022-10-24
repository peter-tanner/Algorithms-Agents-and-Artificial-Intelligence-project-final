from enum import Enum
from math import atan, pi
import matplotlib.pyplot as plt
from etc.custom_float import Uncertainty
from etc.messages import Opinion
from copy import deepcopy
from random import Random
from typing import List, Tuple
import networkx as nx

import agents.red as red
import agents.blue as blue
import agents.gray as gray
import agents.green as green
from play_config import DAYS_UNTIL_ELECTION, ENABLE_GRAPHICS, INITIAL_BLUE_ENERGY, INITIAL_UNCERTAINTY_RANGE


class GameState:
    iteration: int
    winner: "Winner"
    iterations_left: int

    n_green_agents: int
    p_green_agents: float
    green_agents: nx.Graph
    uncertainty_interval: Tuple[Uncertainty]

    gray_agents: List["gray.GrayAgent"]

    red_agent: "red.RedAgent"
    blue_agent: "blue.BlueAgent"
    rand: Random

    # Visualization stuff
    graphics: bool
    viz = {}

    # > At the start of the game, you need an initialise function.
    def __init__(self,
                 green_agents: Tuple[int, float, float],
                 gray_agents: Tuple[int, float],
                 uncertainty_interval: Tuple[Uncertainty],
                 seed: int, graphics: bool = ENABLE_GRAPHICS) -> None:
        """_summary_

        Args:
            green_agents (Tuple[int, float, float]): (number of green agents, probability of connection, probability of initial opinion = blue)
            gray_agents (Tuple[int, float]): (number of gray agents, probability of red spy)
            uncertainty_interval (Tuple[float]): _description_
            seed (int): seed for Random in game
        """
        self.graphics = graphics

        self.iteration = 0
        self.winner = Winner.NO_WINNER

        self.rand = Random()
        self.rand.seed(seed)
        self.uncertainty_interval = uncertainty_interval

        self.n_green_agents = green_agents[0]
        self.p_green_agents = green_agents[1]
        self.green_agents = nx.erdos_renyi_graph(self.n_green_agents, self.p_green_agents)

        # Generate gray agents
        self.gray_agents = []
        for x in range(0, int(gray_agents[0] * gray_agents[1])):
            self.gray_agents.append(gray.GrayAgent(Opinion.BLUE, self.rand))
        for x in range(int(gray_agents[0] * gray_agents[1]), gray_agents[0]):
            self.gray_agents.append(gray.GrayAgent(Opinion.RED, self.rand))

        # > You have to assign one or the other opinion to green.
        # > Percentage of agents (green) who want to vote in the election, at the start of the   [From pdf]

        # > The other variable is uncertainity, for your given interval
        # > (say it was -0.5, 0.5), you need to generate a sequence of random
        # > numbers and assign and then assign green agents a number from that
        # > sequence. For say m green agents, you need m numbers, and there
        # > can be duplicates!
        # Negative numbers can still be "more positive" than lower negative numbers...
        # so translating the interval should have NO EFFECT on the probabilities
        # So we can assume that the uncertainty is in [-1.0,1.0] but this
        # uncertainty interval is only for initialization stage?
        for person in self.green_agents.nodes(data=False):
            uncertainty: Uncertainty = Uncertainty(self.rand.uniform(uncertainty_interval[0], uncertainty_interval[1]))
            polarity = Opinion.RED
            if self.rand.random() < green_agents[2]:
                polarity = Opinion.BLUE
            self.green_agents.nodes[person]['data'] = green.GreenAgent(uncertainty, polarity, self.rand)

        self.blue_agent = blue.BlueAgent(INITIAL_BLUE_ENERGY, self.rand)
        self.red_agent = red.RedAgent(self.n_green_agents, self.rand)
        self.red_agent.red_count, self.blue_agent.blue_count = self.count_majority()

        # Visualization

        self.viz['pos'] = nx.nx_pydot.graphviz_layout(self.green_agents, prog="fdp")

        self.iterations_left = DAYS_UNTIL_ELECTION

    @staticmethod
    def short_init(green_agents: Tuple[int, float], gray_agents: Tuple[int, float]) -> "GameState":
        return GameState(green_agents, gray_agents, INITIAL_UNCERTAINTY_RANGE, None)

    def get_green_agent(self, person: int) -> green.GreenAgent:
        return self.green_agents.nodes[person]['data']

    def close(self) -> None:
        self.blue_agent.update_lut(self)
        self.blue_agent.close_lut()
        self.red_agent.update_lut(self)
        self.red_agent.close_lut()

    def green_round(self: "GameState") -> "GameState":
        next_green_graph: nx.Graph = deepcopy(self.green_agents)
        for person in self.green_agents.nodes(data=False):
            for connection in self.green_agents.neighbors(person):
                # Test nodes
                obj_person: "green.GreenAgent" = self.get_green_agent(person).clone()
                obj_connection: "green.GreenAgent" = self.get_green_agent(connection).clone()
                interaction_result = Opinion.UNDEFINED  # = obj_person.interact(obj_connection)

                # > green team's turn: all agents who have a connection between them
                # > can can have an interaction, the one who is more certain about
                # > their opinion may affect the other green.
                # Source: Help3001
                # > This equation is for this particular paper because they have
                # > the opinion on that.
                # > The opinions are a real number, okay?
                # > And they are on a scale of minus one to
                # > plus one
                # > for your project.
                # > You will also have to write an equation, you have
                # > to come up with your own equation.
                # > Okay, so that is the part of your project.
                # > That equation does not have to be an overly complicated
                # > equation.
                # > Could be a really small equation.
                # > Uh, simple equation.
                # > You can you could be updating.
                # > Um, uh, the uncertainties by a simple, uh, you know,
                # > a small value.
                # > Okay, so just think over it.
                # > How would you like to do that?
                # Source: CITS3001 - 13 Sep 2022, 11:00 - Lecture
                # For context:
                # > Now, in the project, you had, like, two opinions.
                # > Okay, uh, to vote or not to vote.
                # Source: CITS3001 - 13 Sep 2022, 11:00 - Lecture
                next_: green.GreenAgent
                if obj_person.uncertainty < obj_connection.uncertainty:
                    # Switch the other agent
                    # next_connection = next_state.green_agents.nodes[connection]['data']
                    next_connection: green.GreenAgent = next_green_graph.nodes[connection]['data']
                    interaction_result = next_connection.attempt_switch(obj_person.polarity)
                    # Rationale: The more certain an agent is the better they are at arguing,
                    # which causes the target to be more certain about their decision to switch,
                    # although not completely uncertain since they just switched.
                    if not interaction_result == Opinion.UNDEFINED:
                        next_connection.uncertainty -= obj_person.uncertainty.certainty() * green.OPINION_INFLUENCE
                else:
                    # Switch self
                    next_person: green.GreenAgent = next_green_graph.nodes[person]['data']
                    interaction_result = next_person.attempt_switch(obj_connection.polarity)
                    if not interaction_result == Opinion.UNDEFINED:
                        next_person.uncertainty -= obj_connection.uncertainty.certainty() * green.OPINION_INFLUENCE

                # Update totals
                # if interaction_result == Opinion.RED:
                #     self.red_agent.red_count += 1
                #     self.blue_agent.blue_count -= 1
                # elif interaction_result == Opinion.BLUE:
                #     self.red_agent.red_count -= 1
                #     self.blue_agent.blue_count += 1
        self.green_agents = next_green_graph
        self.red_agent.red_count, self.blue_agent.blue_count = self.count_majority()

    #
    # Visualization
    #

    def draw_green_network(self) -> None:
        if not self.graphics:
            return
        labels = {}
        colors = []
        for node in self.green_agents.nodes():
            agent = self.get_green_agent(node)

            label = "F" if agent.following_red else ""
            labels[node] = label

            if agent.polarity == Opinion.RED:
                colors.append((agent.uncertainty.certainty(), 0, 0))
            else:
                colors.append((0, 0, agent.uncertainty.certainty()))
        nx.draw(self.green_agents, node_color=colors, labels=labels, pos=self.viz['pos'], node_size=70)
        plt.savefig("green_graph.png", dpi=600)
        plt.close()

    def count_majority(self) -> Tuple[int, int]:
        red_count: int = 0
        blue_count: int = 0
        for _, person in self.green_agents.nodes(data="data"):
            person: green.GreenAgent
            if person.uncertainty < Uncertainty.UNCERTAINTY_THRESHOLD:
                if person.polarity == Opinion.BLUE:
                    blue_count += 1
                elif person.polarity == Opinion.RED:
                    red_count += 1
        return red_count, blue_count

    def determine_majority(self) -> "Winner":
        if self.red_agent.red_count > self.n_green_agents * 0.9:
            return Winner.RED_WIN
        elif self.blue_agent.blue_count > self.n_green_agents * 0.9:
            return Winner.BLUE_WIN
        return Winner.NO_WINNER

    def update_winner(self) -> None:
        # > In order for the Red agent to win (i.e., a higher number of green agents with
        # > opinion “not vote”, and an uncertainty less than 0 (which means they are
        # > pretty certain about their choice))
        #
        # > In order for the Blue agent to win (i.e., a higher number of green agents with
        # > opinion “vote”, and an uncertainty less than 0 (which means they are pretty
        # > certain about their choice))
        #
        # Higher than what? Assuming it means 50% of the population, otherwise one team can
        # win from the start of the game just by comparing to the same metric but
        # with the other team.
        majority = self.determine_majority()
        if not majority == Winner.NO_WINNER:
            self.winner = majority
            return

        # Blue agent loss:
        # > If they expend all their energy, the game will end
        # Source: Help3001
        # > - blue agent dead
        if self.blue_agent.blue_energy <= 0:
            self.winner = Winner.BLUE_NO_ENERGY
            return

        # Red agent loss:
        # > - red agent lost all followers
        if self.red_agent.red_followers <= 0:
            self.winner = Winner.RED_NO_FOLLOWERS
            return

        self.winner = Winner.NO_WINNER
        return

    def __str__(self) -> str:
        return f"""
{self.iteration=}, {self.winner=}
{self.red_agent.red_followers=}, [{self.blue_agent.blue_energy=}, gray_mean={self.blue_agent.gray_mean()} {self.blue_agent.gray_mem=}]
{self.red_agent.red_count=}, {self.blue_agent.blue_count=}
{str(self.red_agent.last_message)} || {str(self.blue_agent.last_message)}
"""

    def print_gamestate_pretty(self) -> str:
        return f"""
--- ROUND {self.iteration} ---
Population statistics
- People voting (Blue)      {self.blue_agent.blue_count}
- People not voting (Red)   {self.red_agent.red_count}
Agent state
- Blue energy remaining:    {self.blue_agent.blue_energy}
- Red subscribers:          {self.red_agent.red_followers}
Last move
- Red:  {self.red_agent.last_message.message}
- Blue: {self.blue_agent.last_message.message} 
    - Last gray outcome: {"UNDEFINED" if len(self.blue_agent.gray_mem) == 2 else self.blue_agent.gray_mem[-1]}
"""


class Winner(Enum):
    NO_WINNER = 0
    BLUE_WIN = 1
    RED_WIN = 2
    BLUE_NO_ENERGY = 3
    RED_NO_FOLLOWERS = 4

    def red_won(winner: "Winner"):
        return winner in [Winner.BLUE_NO_ENERGY or Winner.RED_WIN]

    def blue_won(winner: "Winner"):
        return winner in [Winner.RED_NO_FOLLOWERS or Winner.RED_WIN]

    def winner_opinion(winner: "Winner"):
        if Winner.red_won(winner):
            return Opinion.RED
        elif Winner.blue_won(winner):
            return Opinion.BLUE
        return Opinion.UNDEFINED
