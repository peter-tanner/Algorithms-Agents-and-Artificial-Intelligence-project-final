
from random import Random
from typing import List
import agents.blue as blue
from agents.green import GreenAgent
import agents.red as red
from etc.messages import Opinion
import etc.gamestate as gs
from etc.messages import Message, BLUE_MESSAGES, RED_MESSAGES


class GrayAgent:
    polarity: Opinion
    weights: List[float]
    rand: Random

    def __init__(self, polarity: Opinion, rand: Random) -> None:
        self.polarity = polarity
        self.rand = rand

    def choose_message(self) -> Message:
        if self.polarity == Opinion.BLUE:
            return self.rand.choices(BLUE_MESSAGES, weights=self.weights, k=1)[0]
        else:
            return self.rand.choices(RED_MESSAGES, weights=self.weights, k=1)[0]

    def gray_action(self, state: "gs.GameState"):
        # TODO: There is no reason for gray not to play the highest potency message
        # as it has no penalty for playing high potency messages.
        if self.polarity == Opinion.BLUE:
            message: Message = BLUE_MESSAGES[4]
            for person in state.green_agents.nodes(data=False):
                obj_person: GreenAgent = state.green_agents.nodes[person]['data']
                blue.BlueAgent.blue_action(obj_person, message)
        else:
            message: Message = RED_MESSAGES[4]
            for person in state.green_agents.nodes(data=False):
                obj_person: GreenAgent = state.green_agents.nodes[person]['data']
                red.RedAgent.red_action(obj_person, message)
