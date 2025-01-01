import io
import logging


class Logger:
    def __init__(self, name: str = "devJob") -> None:
        buffer = io.StringIO()
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        capture = logging.StreamHandler(buffer)
        capture.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        capture.setFormatter(formatter)
        # logger.addHandler(logging.StreamHandler())
        logger.addHandler(capture)
        self.buffer = buffer
        self.logs = logger

    def log(self, message: str) -> None:
        self.logs.info(message)
        print(message)
