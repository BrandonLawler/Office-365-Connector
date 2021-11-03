import logging

class CoreException(Exception):
    """
    Base class for all exceptions raised by the Core module.
    """
    def __init__(self, message, shutdown_event):
        logging.error("Core Exception Occured")
        logging.error(message)
        shutdown_event.set()