from .core import Core
from .messages import Courier
import multiprocessing, os


class Example:
    def __init__(self, process_event: multiprocessing.Event, shutdown_event: multiprocessing.Event, courier: Courier):
        self._process_event = process_event
        self._shutdown_event = shutdown_event
        self._courier = courier
    
    def start(self):
        self._courier.send("Core", "PID", os.getpid())
        while not self._process_event.is_set():
            pass
        self._shutdown_event.set()