import enum


class BlockObject(enum.Enum):
    EMPTY = 0
    FINISH = 1
    MUD = 2
    OIL_SPILL = 3
    WALL = 4
    FLIMSY_WALL = 5
    OIL_POWER = 6
    BOOST = 7
    LIZARD = 8
    TWEET = 9
    EMP = 10


class Direction(enum.Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class Commands(enum.Enum):
    ACCELERATE = "ACCELERATE"
    DECELERATE = "DECELERATE"
    NOTHING = "NOTHING"
    USE_OIL = "USE_OIL"
    USE_BOOST = "USE_BOOST"
    TURN_RIGHT = "TURN_RIGHT"
    TURN_LEFT = "TURN_LEFT"
    USE_TWEET = "USE_TWEET"
    USE_LIZARD = "USE_LIZARD"
    USE_EMP = "USE_EMP"
    FIX = "FIX"

    def __str__(self):return str(self.value)


class State(enum.Enum):
    ACCELERATING = "ACCELERATING"
    READY = "READY"
    NOTHING = "NOTHING"
    TURNING_RIGHT = "TURNING_RIGHT"
    TURNING_LEFT = "TURNING_LEFT"
    HIT_MUD = "HIT_MUD"
    DECELERATING= "DECELERATING"
    PICKED_UP_POWERUP = "PICKED_UP_POWERUP"
    USED_BOOST = "USED_BOOST"
    USED_OIL = "USED_OIL"
    HIT_OIL = "HIT_OIL"
    FINISHED = "FINISHED"
