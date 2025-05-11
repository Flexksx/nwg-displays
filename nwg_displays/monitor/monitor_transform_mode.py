from enum import IntEnum, Enum


class MonitorTransformMode(IntEnum):
    NORMAL = 0
    ROTATE_90 = 1
    ROTATE_180 = 2
    ROTATE_270 = 3
    FLIPPED = 4
    FLIPPED_ROTATE_90 = 5
    FLIPPED_ROTATE_180 = 6
    FLIPPED_ROTATE_270 = 7

    def __str__(self):
        return self.name.replace("_", " ").title()
