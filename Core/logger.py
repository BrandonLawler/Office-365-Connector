import logging
import multiprocessing
from .messages import Courier
import sys


class Logger:
    _LOGFILE = "office365connector.log"
    _LOGFORMAT = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"

    def __init__(self, process_event: multiprocessing.Event, shutdown_event: multiprocessing.Event, courier: Courier, logging_level=None):
        self._process_event = process_event
        self._shutdown_event = shutdown_event
        self._courier = courier

        self._logging_level = logging_level if logging_level is not None else logging.CRITICAL
        try:
            with open(self._LOGFILE, "w") as f:
                pass
        except:
            pass

        self._console_logger = logging.StreamHandler(sys.stderr)
        self._console_logger.setFormatter(logging.Formatter(self._LOGFORMAT))
        self._console_logger.setLevel(self._logging_level)

        self._file_logger = logging.FileHandler(self._LOGFILE)
        self._file_logger.setFormatter(logging.Formatter(self._LOGFORMAT))
        self._file_logger.setLevel(logging.NOTSET)
        self.start()
    
    def log(self, message: str, level: int):
        self._console_logger.log(level, message)
        self._file_logger.log(level, message)        

    def start(self):
        self.log("Starting logger", logging.INFO)
        while not self._process_event.is_set():
            message = self._courier.receive()
            if message is not None:
                self.log(message.type, message.content)
        self._shutdown_event.set()