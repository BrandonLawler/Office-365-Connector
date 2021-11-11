import multiprocessing
from .messages import Central
from .logger import Logger
import logging
import os


class Core:
    def __init__(self, loglevel=logging.INFO):    
        self._process_event = multiprocessing.Event()
        self._process_ids = []
        self._shutdowns = []
        self._process_count = 0
        self._process_list = {}
        self._loglevel = loglevel
        self._central = None
        self._courier = None
        self.create_central_process()
        self.create_logging_process()
    
    def create_central_process(self):
        shutdown = multiprocessing.Event()
        self._shutdowns.append(shutdown)
        self._process_count += 1
        self._central = Central(self._process_event, shutdown)
        self._courier = self._central.create_queue("Core")
        self._process_list['Central'] = multiprocessing.Process(target=self._central.start)
        self._courier.log(f"Core: Central Process Created", logging.INFO)
    
    def create_logging_process(self):
        shutdown = multiprocessing.Event()
        self._shutdowns.append(shutdown)
        self._process_count += 1
        process_args = [
            self._process_event,
            shutdown,
            self._central.create_queue("Logger")
        ]
        process_kwargs = {
            "logging_level": self._loglevel
        }
        self._process_list['Logger'] = multiprocessing.Process(target=Logger, args=process_args, kwargs=process_kwargs)

    def create_process(self, process_name, process_function, process_args=None, process_kwargs=None):
        if process_args is None:
            process_args = []
        if process_kwargs is None:
            process_kwargs = {}
        shutdown = multiprocessing.Event()
        self._shutdowns.append(shutdown)
        process_args.insert(0, self._process_event)
        process_args.insert(1, shutdown)
        process_args.insert(2, self._central.create_queue(process_name))
        self._process_count += 1
        self._process_list[process_name] = multiprocessing.Process(target=process_function, args=process_args, kwargs=process_kwargs)
        self._courier.log(f"Core: Process Created {process_name}", logging.INFO)
        self._courier.log(f"Core: Process Created Parameters {process_args}", logging.DEBUG)
    
    def check_message(self):
        message = self._courier.receive()
        if message is not None:
            self._courier.log(f"Core: Message Received {message}", logging.DEBUG)
            if message.type == "PID":
                self._process_ids.append(message.content)
        # if not self._central_queue.empty():
        #     message = self._central_queue.get()
        #     # self._logger.info(f"Core: Message Received {message}")
        #     if message.type == "PID":
        #         self._process_ids.append(message.content)

    def check_shutdowns(self):
        shutdown_count = self._process_count
        for shutdown in self._shutdowns:
            if shutdown.is_set():
                shutdown_count -= 1
        return shutdown_count
    
    def check_pids(self):
        process_died = False
        for pid in self._process_ids:
            try:
                os.kill(pid, 0)
            except OSError:
                process_died = True
                self._courier.log(f"Core: Process Died {pid}", logging.ERROR)
        return process_died
    
    def start(self):
        for process_name, process in self._process_list.items():
            process.start()
            self._courier.log(f"Core: Process Started {process_name}", logging.INFO)
        while not self._process_event.is_set():
            self._process_event.wait(1)
            if self.check_shutdowns() != self._process_count:
                self._courier.log(f"Core: Shutting Detected", logging.DEBUG)
                self._process_event.set()
            if self.check_pids():
                self._courier.log(f"Core: Process Died", logging.ERROR)
                self._process_event.set()
            self.check_message()
        for process_name, process in self._process_list.items():
            process.join()
            self._courier.log(f"Core: Process Joined {process_name}", logging.INFO)
        self._courier.log(f"Core: Shutting Down", logging.INFO)
        while True:
            if self.check_shutdowns() == 0:
                break
        