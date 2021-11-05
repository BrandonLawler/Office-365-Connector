import multiprocessing, logging

class PowerShellException(Exception):
    """
    Base class for all exceptions raised by the Core module.
    """
    def __init__(self, message, shutdown_event=None):
        self._logger = multiprocessing.get_logger()
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())

        self._logger.error("PowerShell Exception Occured")
        self._logger.error(message)

        if shutdown_event is not None:
            shutdown_event.set()