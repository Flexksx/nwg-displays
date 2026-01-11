from enum import StrEnum


class MonitorTransformMode(StrEnum):
    NORMAL = "normal"
    ROTATE_90 = "90"
    ROTATE_180 = "180"
    ROTATE_270 = "270"
    FLIPPED = "flipped"
    FLIPPED_ROTATE_90 = "flipped-90"
    FLIPPED_ROTATE_180 = "flipped-180"
    FLIPPED_ROTATE_270 = "flipped-270"

    def __str__(self):
        return self.name.replace("_", " ").title()
