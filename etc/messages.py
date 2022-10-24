from enum import Enum
from math import nan
from typing import Union, overload
from etc.custom_float import Uncertainty

from play_config import INITIAL_UNCERTAINTY_RANGE


class Opinion(Enum):
    RED = 0
    BLUE = 1
    UNDEFINED = 2

    def opposite(opinion: "Opinion"):
        return Opinion.RED if opinion == Opinion.BLUE else Opinion.BLUE

    def __str__(self) -> str:
        return {
            Opinion.RED: "RED",
            Opinion.BLUE: "BLUE",
            Opinion.UNDEFINED: "?",
        }[self]


# > Sometimes people say that we would like to just model
# > it by 01.
# > Okay, They're very uncertain.
# > Would be zero and very certain would be won.
# > Okay, you can do that.
# > Okay.
# > So it depends upon your understanding.
# > All right?
# > Yes.
# Source: CITS3001 - 13 Sep 2022, 11:00 - Lecture

INFLUENCE_FACTOR = 1.0


class Message():
    id: int
    potency: Uncertainty
    cost: float
    message: str

    def __init__(self, id: int, message: str, potency: float, cost: float) -> None:
        self.id = id
        self.cost = cost
        self.potency = Uncertainty(potency)
        self.message = message

    def __str__(self) -> str:
        return f"{self.potency=}, {self.cost=}, {self.message}"


MESSAGE_UNDEFINED = Message(0, "UNDEFINED", 0.0, 0.0)


# > So why did I mention that you need to have
# > five levels or 10 levels?
# > It was for simplicity, because this is how we normally
# > start the project.
# > If you just want five or 10 levels, that's fine.
# > I'm not going to detect points for that.
# Source: CITS3001 - 13 Sep 2022, 11:00 - Lecture
#
# > And then what else you need to have is for
# > every uncertainty value, either you need to have this in
# > a table, or you just need to define it by
# > an equation.
# Source: CITS3001 - 13 Sep 2022, 11:00 - Lecture
# Using a lookup-table

mul1 = 1
potencymul1 = 0.05
RED_MESSAGES = [
    Message(0, "Red message (low)", potencymul1 * 0.1, 0.1 / mul1),
    Message(1, "Red message (medlow)", potencymul1 * 0.15, 0.15 / mul1),
    Message(2, "Red message (med)", potencymul1 * 0.2, 0.2 / mul1),
    Message(3, "Red message (highmed)", potencymul1 * 0.25, 0.25 / mul1),
    Message(4, "Red message (high)", potencymul1 * 0.3, 0.3 / mul1),
]

MESSAGE_BLUE_SPY = Message(0, "Gray spy - chance of highest red OR blue message, at no cost", nan, 0.0)
mul2 = 1
potencymul2 = 0.05
BLUE_MESSAGES = [
    Message(0, "Blue message (low)", potencymul2 * 0.5 * 0.1, 0.1 / mul2),
    Message(1, "Blue message (medlow)", potencymul2 * 0.5 * 0.15, 0.15 / mul2),
    Message(2, "Blue message (med)", potencymul2 * 0.5 * 0.2, 0.2 / mul2),
    Message(3, "Blue message (highmed)", potencymul2 * 0.5 * 0.25, 0.25 / mul2),
    Message(4, "Blue message (high)", potencymul2 * 0.5 * 0.3, 0.3 / mul2),
]
