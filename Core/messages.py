from multiprocessing import Queue
import logging
from .exceptions import CoreException


class Message:
    def __init__(self, recipient, message_type, message_content):
        self.sender = None
        self.recipient = recipient
        self.type = message_type
        self.content = message_content
    
    def __str__(self):
        return f"{self.sender} -> {self.recipient} ({self.type}): {self.content}"
    

class Courier:
    _RECEIVE_TIMEOUT = 1

    def __init__(self, process_name, sender_queue: Queue, receiver_queue: Queue):
        self.process_name = process_name
        self.send_queue = sender_queue
        self.receiver_queue = receiver_queue

    def send(self, message: Message):
        message.sender = self.process_name
        logging.info(f"{self.process_name} sending message to {message.recipient}")
        logging.debug(f"{self.process_name} sending message: {message}")
        self.send_queue.put(message)

    def receive(self: Message):
        message = self.receiver_queue.get(timeout=self._RECEIVE_TIMEOUT)
        if message is None:
            return None
        logging.info(f"{self.process_name} received message from {message.sender}")
        logging.debug(f"{self.process_name} received message: {message}")
        return message


class Central:
    _MAX_QUEUE_SIZE = 10
    _RECEIVE_TIMEOUT = 1

    def __init__(self, process_running, shutdown_event, core_queue):
        self._process_running = process_running
        self._shutdown_event = shutdown_event
        self._core_queue = core_queue
        self._send_queues = {}
        self._receive_queues = {}
    
    def create_queue(self, queue_name):
        if queue_name not in self._receive_queues and queue_name not in self._send_queues:
            self._send_queues[queue_name] = Queue(maxsize=self._MAX_QUEUE_SIZE)
            self._receive_queues[queue_name] = Queue(maxsize=self._MAX_QUEUE_SIZE)
            return Courier(queue_name, self._send_queues[queue_name], self._receive_queues[queue_name])
        raise CoreException("Queue already exists", self._shutdown_event)
    
    def start(self):
        while self._process_running.is_set():
            for queue_name in self._receive_queues:
                message = self._receive_queues[queue_name].get(timeout=self._RECEIVE_TIMEOUT)
                if message is not None:
                    logging.info(f"Central received message from {message.sender}")
                    logging.debug(f"Central received message: {message}")
                    if message.recipient == "Core":
                        self._core_queue.put(message)
                    elif message.recipient in self._receive_queues:
                        self._receive_queues[message.recipient].put(message)
                    else:
                        logging.warning(f"{message.recipient} not found in queues")
        self._shutdown_event.set()
