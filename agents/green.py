
from random import Random
from typing import Tuple
from etc.custom_float import Uncertainty
from etc.messages import Opinion

OPINION_INFLUENCE = 0.2


class GreenAgent:
    uncertainty: Uncertainty
    polarity: Opinion
    following_red: bool
    rand: Random

    def __init__(self, uncertainty: float, polarity: Opinion, rand: Random) -> None:
        self.uncertainty = uncertainty
        self.polarity = polarity
        self.following_red = True
        self.rand = rand

    def attempt_swap(self):
        # > To make it simple, the more positive a value is the more uncertain the
        # > agent is and the more negative the value is the more certain the agent is
        # Source: Help3001
        if self.rand.uniform(Uncertainty.UNCERTAINTY_MIN, Uncertainty.UNCERTAINTY_MAX) < self.uncertainty:
            self.polarity = Opinion.opposite(self.polarity)

    def attempt_switch(self, polarity: Opinion) -> Opinion:
        # > To make it simple, the more positive a value is the more uncertain the
        # > agent is and the more negative the value is the more certain the agent is
        # Source: Help3001
        if self.rand.uniform(Uncertainty.UNCERTAINTY_MIN, Uncertainty.UNCERTAINTY_MAX) < self.uncertainty:
            self.polarity = polarity
            return polarity
        return Opinion.UNDEFINED

    def unfollow_red(self):
        self.following_red = False

    def clone(self) -> "GreenAgent":
        return GreenAgent(self.uncertainty.clone(), self.polarity, self.rand)
