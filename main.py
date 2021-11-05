from Core.core import Core
from Interface.app import App
import logging
import multiprocessing

if __name__ == '__main__':
    core = Core()
    # put process code here
    core.create_process("Interface", App)

    core.start()
    