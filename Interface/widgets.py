import os
from PyQt6.QtWidgets import QPushButton, QLabel, QProgressBar, QMainWindow, QWidget
from PyQt6.QtGui import QIcon, QMovie
from PyQt6.QtCore import *


class MainWindow(QMainWindow):
    def __init__(self, close_event):
        super().__init__()
        self._onclose = close_event

    def closeEvent(self, event):
        self._onclose()


class Widget(QWidget):
    def __init__(self, objname=None, stylestring=None):
        super().__init__()
        if objname is not None:
            self.setObjectName(objname)
        if stylestring is not None:
            self.setStyleSheet(stylestring)


class Button(QPushButton):
    def __init__(self, text, onclick=None, objname=None, stylestring=None):
        super().__init__(text)
        if objname is not None:
            self.setObjectName(objname)
        if stylestring is not None:
            self.setStyleSheet(stylestring)
        self._onclick = onclick
        self.clicked.connect(onclick)
    
    def on_click(self):
        if self._onclick is not None:
            self._onclick()


class SwitchButton(Button):
    def __init__(self, text, onclick=None, ontoggle=None, objname=None, stylestring=None):
        super().__init__(text, onclick, objname, stylestring)
        self.setCheckable(True)
    
    def on_click(self):
        if self._onclick is not None:
            self._onclick()
        if self._ontoggle is not None:
            self._ontoggle()


class Label(QLabel):
    def __init__(self, text, objname=None, stylestring=None):
        super().__init__(text)
        if objname is not None:
            self.setObjectName(objname)
        if stylestring is not None:
            self.setStyleSheet(stylestring)


class Movie(QMovie):
    def __init__(self, path, objname=None, stylestring=None):
        super().__init__(path)
        if objname is not None:
            self.setObjectName(objname)
        if stylestring is not None:
            self.setStyleSheet(stylestring)
