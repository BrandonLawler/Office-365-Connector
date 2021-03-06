import multiprocessing, logging

class CoreException(Exception):
    """
    Base class for all exceptions raised by the Core module.
    """
    def __init__(self, message, shutdown_event):
        self._logger = multiprocessing.get_logger()
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())

        self._logger.error("Core Exception Occured")
        self._logger.error(message)
        shutdown_event.set()