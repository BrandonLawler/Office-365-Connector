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
    _MEDIA_PATH = f"{os.getcwd()}\\Interface\\media"

    _WINDOW_HEIGHT = 600
    _WINDOW_WIDTH = 860
    _LOADING_WINDOW_HEIGHT = 80
    _LOADING_WINDOW_WIDTH = 60

    _INITIALISATION_CHECKS = [
        "Initialising Exchange Online",
        "Initialising Microsoft 365 Online"
    ]

    _STAGE_INITIALISATION = 0
    _STAGE_DISCONNECTED = 1

    def __init__(self, process_event: multiprocessing.Event, shutdown_event: multiprocessing.Event, courier: Courier):
        self._logger = multiprocessing.get_logger()
        # self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())
        
        self._process_event = process_event
        self._shutdown_event = shutdown_event
        self._courier = courier
        self._courier.send("Core", "PID", os.getpid())

        self._mainframe = None
        self._body = None
        self._body_frame = None

        self._customization = None
        self._mode = 0

        self._movie = None
        self._loading_label = None
        self._loading_bar = None

        self._shutdown_timer = QTimer()
        self._shutdown_timer.timeout.connect(self._shutdown_application)
        self._shutdown_timer.setInterval(1000)

        self._message_timer = QTimer()
        self._message_timer.timeout.connect(self._message_process)
        self._message_timer.setInterval(100)

        self._initialise()
        self._build()
        self._courier.send("O365", "Initialise")
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
    
    def _message_process(self):
        message = self._courier.receive()
        if message is not None:
            if message.type == "Initalise":
                if type(message.content) is int:
                    self._loading_bar.setValue(message.content)
                    if message.content == self._INITIALISATION_CHECKS.__len__():
                        self._mode = self._STAGE_DISCONNECTED
                        self._window.resize(self._WINDOW_WIDTH, self._WINDOW_HEIGHT)
                    else:
                        self._loading_label.setText(self._INITIALISATION_CHECKS[message.content-1])
                else:
                    raise Exception("Unable to Initialise PowerShell Modules")
            elif message.type == "Check Customization":
                self._customization = message.content

    def _initialise(self):
        self._application = QApplication([])

        self._window = MainWindow(self._shutdown)
        self._window.setWindowTitle(self._TITLE)
        self._window.setMinimumSize(self._WINDOW_WIDTH, self._WINDOW_HEIGHT)
        self._window.setMaximumSize(self._WINDOW_WIDTH, self._WINDOW_HEIGHT)

        self._mainframe = QFrame()
        self._window.setCentralWidget(self._mainframe)

    def _build_variable_display(self, *args, horizontal=False, vertical=False, grid=False):
        frame_container = Widget()
        if horizontal:
            frame = QHBoxLayout(frame_container)
        elif vertical:
            frame = QVBoxLayout(frame_container)
            frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif grid:
            frame = QGridLayout(frame_container)
        else:
            raise ValueError("Invalid Layout Type: Horizontal, Vertical or Grid input must be specified")
        frame.setSpacing(0)
        frame.setContentsMargins(10, 0, 10, 10)
        for arg in args:
            if grid:
                try:
                    widget, row, column, rsize, csize = arg
                    frame.addWidget(widget, row, column, rsize, csize)
                except:
                    raise ValueError("Invalid Grid Layout: Must be (Widget, row, column, row_size, column_size)")
            else:
                if vertical:
                    arg.setAlignment(Qt.AlignmentFlag.AlignCenter)
                frame.addWidget(arg)
        return frame_container
    
    def _build(self):
        self._mainframe.setLayout(QVBoxLayout())
        self._mainframe.layout().addWidget(self._build_header())
        self._mainframe.layout().addWidget(self._build_body())
        self._mainframe.layout().addWidget(self._build_footer())
    
    def _build_loading_frame(self, message):
        self._logger.debug("Building Loading Frame")

        self._movie = Movie(f"{self._MEDIA_PATH}\\loading_icon.gif", 120)
        loading_movie = Label("")
        loading_movie.setMovie(self._movie)

        loading_label = Label(message)

        self._loading_bar = ProgressBar(0, self._INITIALISATION_CHECKS.__len__())

        return self._build_variable_display(loading_movie, loading_label, self._loading_bar, vertical=True, horizontal=False, grid=False)   
    
    def _build_initialisation(self):
        self._window.resize(self._LOADING_WINDOW_WIDTH, self._LOADING_WINDOW_HEIGHT)
        return self._build_loading_frame("Initialising PowerShell Modules")
    
    def _build_header(self):
        header = QFrame()
        header.setLayout(QHBoxLayout())
        


        return header
    
    def _build_body(self):
        self._body = QFrame()
        self._body.setLayout(QVBoxLayout())

        if self._body_frame is not None:
            self._body_frame.hide()
        
        if self._mode == self._STAGE_INITIALISATION:
            self._body_frame = self._build_initialisation()
        self._body.layout().addWidget(self._body_frame)
        
        return self._body
    
    def _build_footer(self):
        footer = QFrame()
        footer.setLayout(QHBoxLayout())
        # footer.layout().addWidget(self._build_version())
        # footer.layout().addWidget(self._build_copyright())

        return footer
    
    def start(self):
        self._window.show()
        if self._movie is not None:
            self._movie.start()
        self._shutdown_timer.start()
        sys.exit(self._application.exec())
