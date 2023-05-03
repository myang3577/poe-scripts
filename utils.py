import logging
import sys


class Utils:
    @staticmethod
    def setup_logging():
        root = logging.getLogger()
        root.setLevel(logging.INFO)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)s - %(message)s"
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)
