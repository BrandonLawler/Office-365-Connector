import logging
import multiprocessing
from typing import MutableMapping
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from Core.messages import Courier, Message
from .widgets import *
import os, sys


class App:
    _TITLE = 'Office 365 Connector'

    _WINDOW_HEIGHT = 600
    _WINDOW_WIDTH = 860

    def __init__(self, process_event: multiprocessing.Event, shutdown_event: multiprocessing.Event, courier: Courier):
        self._logger = multiprocessing.get_logger()
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())
        
        self._process_event = process_event
        self._shutdown_event = shutdown_event
        self._courier = courier
        self._courier.send("Core", "PID", os.getpid())

        self._mainframe = None
        self._body = None

        self._shutdown_timer = QTimer()
        self._shutdown_timer.timeout.connect(self._shutdown_application)
        self._shutdown_timer.setInterval(1000)

        self._initialise()

        self.start()
    
    def _shutdown(self):
        self._logger.info("PyQt Application Shutting Down")
        self._shutdown_event.set()
        while not self._process_event.is_set():
            pass
    
    def _shutdown_application(self):
        if self._process_event.is_set():
            self._logger.info("Externally Shutting Down Application")
            self._application.quit()

    def _initialise(self):
        self._application = QApplication([])

        self._window = MainWindow(self._shutdown)
        self._window.setWindowTitle(self._TITLE)
        self._window.setMinimumSize(self._WINDOW_WIDTH, self._WINDOW_HEIGHT)
        self._window.setMaximumSize(self._WINDOW_WIDTH, self._WINDOW_HEIGHT)

        self._mainframe = QFrame()
        self._window.setCentralWidget(self._mainframe)
    
    def _build(self):
        self._mainframe.setLayout(QVBoxLayout())
        self._mainframe.layout().addWidget(self._build_header())
        self._mainframe.layout().addWidget(self._build_body())
        self._mainframe.layout().addWidget(self._build_footer())
    
    def _build_header(self):
        header = QFrame()
        header.setLayout(QHBoxLayout())
        


        return header
    
    def _build_body(self):
        self._body = QFrame()
        self._body.setLayout(QVBoxLayout())
        

        
        return self._body
    
    def _build_footer(self):
        footer = QFrame()
        footer.setLayout(QHBoxLayout())
        # footer.layout().addWidget(self._build_version())
        # footer.layout().addWidget(self._build_copyright())

        return footer
    
    def start(self):
        self._window.show()
        self._shutdown_timer.start()
        sys.exit(self._application.exec())
