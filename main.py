from Core.core import Core
from Interface.app import App
from O365.o365 import O365
import logging
import multiprocessing

if __name__ == '__main__':
    core = Core()
    # put process code here
    core.create_process("O365", O365)
    core.create_process("Interface", App)

    core.start()
    