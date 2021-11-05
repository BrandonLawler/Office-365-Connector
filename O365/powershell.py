from .exceptions import *
import subprocess
import logging
import os
import multiprocessing
import threading
import time


def watch_output(pipe, queue):
    print("watching")
    for line in iter(pipe.readline, b''):
        queue.put(line)


class PowerShell:
    """
    
    """
    _SCRIPT_PATH = f"{os.getcwd()}\\..\\PowerShell Scripts"
    _SCRIPT_SEGMENT_PATH = f"{os.getcwd()}\\..\\PowerShell Scripts\\Segments"
    
    _POWERSHELL_COMMAND = 'powershell.exe'
    _QUEUE_TIMEOUT = 0.1

    def __init__(self, shutdown_event):
        self._logger = multiprocessing.get_logger()
        self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())

        self._shutdown_event = shutdown_event

        self._logger.debug("Starting PowerShell")
        self._process = subprocess.Popen(self._POWERSHELL_COMMAND, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        self._queue = multiprocessing.Queue()
        self._thread = threading.Thread(target=watch_output, args=(self._process.stdout, self._queue))
        self._thread.daemon = True
        self._thread.start()

        self._error_queue = multiprocessing.Queue()
        self._error_thread = threading.Thread(target=watch_output, args=(self._process.stderr, self._error_queue))
        self._error_thread.daemon = True
        self._error_thread.start()

        self.readall()
    
    def write(self, script):
        if '\n' not in script:
            script += '\n'
        self._logger.info(f"Writing to PowerShell: {script}")
        self._process.stdin.write(script.encode('utf-8'))
        self._process.stdin.flush()
    
    def read(self, timeout=0.1, script=None):
        start = time.time()
        while True:
            if not self._queue.empty():
                process = False
                if script is None:
                    process = True
                read = self._queue.get(timeout=self._QUEUE_TIMEOUT)
                if script != None and script not in read.decode('utf-8'):
                    process = True
                if process:
                    self._logger.info(f"Reading from PowerShell: {read}")
                    return read.decode('utf-8')
            elif time.time() - start > timeout:
                break
        return None
            
    def check_error(self, timeout=0.1):
        start = time.time()
        while True:
            if not self._error_queue.empty():
                error = self._error_queue.get(timeout=self._QUEUE_TIMEOUT)
                self._logger.error(f"Error from PowerShell: {error}")
                return error
            elif time.time() - start > timeout:
                break
        return False
    
    def readall(self, wait_for_read=True, script=None):
        received = False
        lines = []
        while True:
            line = self.read(script=script)
            if line != None:
                line = line.replace('\r', '').replace('\n', '')
                if line != '':
                    received = True
                    lines.append(line)
            elif not wait_for_read or received:
                break
            else:
                error = self.check_error()
                if error is not False:
                    raise PowerShellException(error, self._shutdown_event)
        return lines
    
    def run_command(self, script):
        self.write(script)
        try:
            return self.readall(script=script)
        except:
            return False
    
    def close(self):
        self._logger.debug("Closing PowerShell")
        self._process.stdin.close()
        self._process.stdout.close()
        self._process.stderr.close()
        self._process.terminate()
    
    def _run_script(self, script_name, wait_response=True, **kwargs):
        lines = []
        with open(script_name, 'r') as script:
            for line in script:
                if '$' in line:
                    for key, value in kwargs.items():
                        line = line.replace(f'${key}', value)
                self.write(line)
                if wait_response:
                    lines.extend(self.readall(script=line))
        return lines
    
    def run_script(self, script_name, wait_response=True, **kwargs):
        return self._run_script(f"{self._SCRIPT_PATH}\\{script_name}", wait_response, **kwargs)
    
    def run_script_segment(self, script_name, wait_response=True, **kwargs):
        return self._run_script(f"{self._SCRIPT_SEGMENT_PATH}\\{script_name}", wait_response, **kwargs)
