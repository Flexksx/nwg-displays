from enum import IntEnum, Enum


class MonitorTransformMode(IntEnum):
    NONE = 0
    ROTATE_90 = 1
    ROTATE_180 = 2
    ROTATE_270 = 3
    FLIP_X = 4
    FLIP_Y = 5

    def __str__(self):
        return self.name.replace("_", " ").title()
