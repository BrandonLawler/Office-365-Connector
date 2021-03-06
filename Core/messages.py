from multiprocessing import Queue
import multiprocessing
import logging
from .exceptions import CoreException
import time
import queue
from fastcore.all import *


class Message:
    def __init__(self, recipient, message_type, message_content=None):
        self.sender = None
        self.recipient = recipient
        self.type = message_type
        self.content = message_content
    
    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.type}): {self.content}"
    

class Courier:
    _RECEIVE_TIMEOUT = 1

    def __init__(self, process_name, sender_queue: Queue, receiver_queue: Queue):
        self._logger = multiprocessing.get_logger()
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())

        self.process_name = process_name
        self.send_queue = sender_queue
        self.receiver_queue = receiver_queue

    @typedispatch
    def send(self, message: Message):
        message.sender = self.process_name
        if message.recipient != "Logger":
            self.log(f"{self.process_name} sending message to {message.recipient}", logging.INFO)
            self.log(f"{self.process_name} sending message: {message}", logging.DEBUG)
        self.send_queue.put(message)

    @typedispatch
    def send(self, recipient: str, message_type, message_content=None):
        self.send(Message(recipient, message_type, message_content))
    
    def log(self, message, level=logging.INFO):
        self.send(Message("Logger", message, level))

    def receive(self, timeout=_RECEIVE_TIMEOUT) -> Message:
        start = time.time()
        while time.time() - start < timeout:
            try:
                message = self.receiver_queue.get(timeout=timeout)
                self.log(f"{self.process_name} received message from {message.sender}", logging.INFO)
                self.log(f"{self.process_name} received message: {message}", logging.DEBUG)
                return message
            except queue.Empty:
                pass
        return None


class Central:
    _MAX_QUEUE_SIZE = 10
    _RECEIVE_TIMEOUT = 1

    def __init__(self, process_running, shutdown_event):
        self._logger = multiprocessing.get_logger()
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())

        self._process_running = process_running
        self._shutdown_event = shutdown_event
        self._send_queues = {}
        self._receive_queues = {}
    
    def create_queue(self, queue_name) -> Courier:
        if queue_name not in self._receive_queues and queue_name not in self._send_queues:
            self._send_queues[queue_name] = Queue(maxsize=self._MAX_QUEUE_SIZE)
            self._receive_queues[queue_name] = Queue(maxsize=self._MAX_QUEUE_SIZE)
            return Courier(queue_name, self._receive_queues[queue_name], self._send_queues[queue_name])
        raise CoreException("Queue already exists", self._shutdown_event)
    
    def start(self):
        self._logger.info("Central Process Starting")
        while not self._process_running.is_set():
            for queue_name in self._receive_queues:
                if not self._receive_queues[queue_name].empty():
                    message = self._receive_queues[queue_name].get(timeout=self._RECEIVE_TIMEOUT)
                    if message is not None:
                        self._receive_queues["Logger"].put(Message("Logger", f"Central received message from {message.sender}", logging.INFO))
                        self._receive_queues["Logger"].put(Message("Logger", f"Central received message: {message}", logging.DEBUG))
                        if message.recipient in self._receive_queues:
                            self._receive_queues[message.recipient].put(message)
                        else:
                            self._receive_queues["Logger"].put(Message("Logger", f"{message.recipient} not found in queues", logging.ERROR))
                            
        self._logger.debug("Central shutdown")
        self._shutdown_event.set()
