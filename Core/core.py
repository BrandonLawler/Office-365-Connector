import multiprocessing
import logging
from .messages import Central
import os


class Core:
    def __init__(self):
        self._logger = multiprocessing.get_logger()
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())
        
        self._process_event = multiprocessing.Event()
        self._process_ids = []
        self._central_queue = multiprocessing.Queue()
        self._shutdowns = []
        self._process_count = 0
        self._process_list = {}
        self._central = None
        self.create_central_process()
    
    def create_central_process(self):
        shutdown = multiprocessing.Event()
        self._shutdowns.append(shutdown)
        self._process_count += 1
        self._central = Central(self._process_event, shutdown, self._central_queue)
        self._process_list['Central'] = multiprocessing.Process(target=self._central.start)
        self._logger.info(f"Core: Central Process Created")

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
        self._logger.info(f"Core: Process Created {process_name} -> {process_function}")
        self._logger.debug(f"Core: Process Created Parameters {process_args} : {process_kwargs}")
    
    def check_message(self):
        if not self._central_queue.empty():
            message = self._central_queue.get()
            self._logger.info(f"Core: Message Received {message}")
            if message.message_type == "PID":
                self._process_ids.append(message.message_content)

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
                self._logger.error(f"Core: Process Died {pid}")
        return process_died
    
    def start(self):
        for process_name, process in self._process_list.items():
            process.start()
            self._logger.info(f"Core: Process Started {process_name}")
        while not self._process_event.is_set():
            self._process_event.wait(1)
            if self.check_shutdowns() != self._process_count:
                self._logger.debug("Process Shutdown Detected")
                self._process_event.set()
            if self.check_pids():
                self._logger.error("Process Died")
                self._process_event.set()
            self.check_message()
        for process_name, process in self._process_list.items():
            process.join()
            self._logger.info(f"Core: Process Joined {process_name}")
        self._logger.info("Core: Shutting Down")
        while True:
            if self.check_shutdowns() == 0:
                break
        
        