import logging


class ClassLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        classname = self.extra.get("classname", "")
        msg = f"[{classname}] {msg}"
        return msg, kwargs


logger = logging.getLogger("nwg-displays")
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("nwg_displays.log")
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_class_logger(cls: type) -> logging.LoggerAdapter:
    return ClassLoggerAdapter(logger, {"classname": cls.__name__})
