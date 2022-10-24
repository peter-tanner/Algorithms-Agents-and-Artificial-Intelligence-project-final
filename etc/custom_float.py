

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

# Custom float class which clamps at ends
class Uncertainty(float):
    UNCERTAINTY_MIN = 0.0
    UNCERTAINTY_MAX = 1.0
    UNCERTAINTY_THRESHOLD = 0.2  # Threshold at which a person is "convinced" by their opinion and can be counted as either "voting" or "not voting"

    def __init__(self, value: float):
        float.__init__(value)
        if value.imag != 0.0:
            raise ValueError("Must be real")
        if value > Uncertainty.UNCERTAINTY_MAX or value < Uncertainty.UNCERTAINTY_MIN:
            raise ValueError("Outside of range")

    def clamp(__x):
        return max(min(__x, Uncertainty.UNCERTAINTY_MAX), Uncertainty.UNCERTAINTY_MIN)

    def short_init(__x) -> "Uncertainty":
        return Uncertainty(Uncertainty.clamp(__x))

    def __add__(self, __x) -> "Uncertainty":
        return Uncertainty.short_init(self.real + __x)

    def __sub__(self, __x) -> "Uncertainty":
        return Uncertainty.short_init(self.real - __x)

    def __rsub__(self, __x) -> "Uncertainty":
        return Uncertainty.short_init(__x - self.real)

    def __radd__(self, __x) -> "Uncertainty":
        return self.__add__(__x)

    def __mul__(self, __x) -> "Uncertainty":
        return Uncertainty.short_init(self.real * __x)

    def certainty(self) -> float:
        return Uncertainty.UNCERTAINTY_MAX - self.real + Uncertainty.UNCERTAINTY_MIN

    def clone(self) -> "Uncertainty":
        return Uncertainty(self.real)


# > All right, So what you need to do is that
# > after every interaction, if the opinion changes, then you need
# > to change uncertainty value as well.
# > All right, So, um, and this is the tricky part
# Source: CITS3001 - 13 Sep 2022, 11:00 - Lecture
#
#
# > the project we have just
# > two opinions, and you need to come up with a
# > way to change the uncertainty.
# Source: CITS3001 - 13 Sep 2022, 11:00 - Lecture
