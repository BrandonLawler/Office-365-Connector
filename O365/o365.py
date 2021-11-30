from Core.messages import Courier
from .exceptions import PowerShellException
from .powershell import PowerShell
import multiprocessing
import logging
import os
import time


class O365:
    _POWERSHELL_MODULE_INSTALLATION_TIMEOUT = 60

    def __init__(self, process_event: multiprocessing.Event, shutdown_event: multiprocessing.Event, courier: Courier):
        self._logger = multiprocessing.get_logger()
        # self._logger.setLevel(logging.DEBUG)
        self._logger.addHandler(logging.StreamHandler())

        self._process_event = process_event
        self._shutdown_event = shutdown_event
        self._courier = courier
        self._courier.send("Core", "PID", os.getpid())
        
        self._powershell = PowerShell(self._shutdown_event)
        self.start()
    
    def _check_exchange_management_installed(self):
        """
        Check if Exchange Management is installed
        """
        response = self._powershell.run_command('Get-InstalledModule -Name ExchangeOnlineManagement')
        if response is False:
            return False
        return True
    
    def _check_microsoft_management_installed(self):
        """
        Check if Microsoft Management is installed
        """
        response = self._powershell.run_command('Get-InstalledModule -Name MSOnline')
        if response is False:
            return False
        return True
    
    def _install_exchange_management(self):
        """
        Install Exchange Management
        """
        start = time.time()
        try:
            self._powershell.run_command('Install-Module -Name ExchangeOnlineManagement -force')
        except PowerShellException:
            pass
        while not self._check_exchange_management_installed():
            if time.time() - start > self._POWERSHELL_MODULE_INSTALLATION_TIMEOUT:
                self._logger.error("Exchange Management installation timed out")
                raise PowerShellException("Exchange Management installation timed out")
    
    def _install_microsoft_management(self):
        """
        Install Microsoft Management
        """
        start_time = time.time()
        try:
            self._powershell.run_command('Install-Module -Name MSOnline -force')
        except PowerShellException:
            pass
        while not self._check_microsoft_management_installed():
            if time.time() - start_time > self._POWERSHELL_MODULE_INSTALLATION_TIMEOUT:
                self._logger.error("Microsoft Management installation timed out")
                raise PowerShellException("Microsoft Management installation timed out")

    def _connect_exchange_management(self, userPrincipleName):
        """
        Connect to Exchange Management
        """
        self._powershell.run_script_segment('Exchange-Connect.ps1', userPrincipleName=userPrincipleName)
    
    def _disconnect_exchange_management(self):
        """
        Disconnect from Exchange Management
        """
        self._powershell.run_script_segment('Exchange-Disconnect.ps1')

    def check_exchange_customization(self):
        """
        Check if Exchange Customization is installed
        """
        response = self._powershell.run_script_segment('Check-Customization.ps1')
        print(f"Customization: {response}")
        if 'True' in response:
            return True
        return False

    def initialise_module(self):
        """
        Initialise the module
        """
        if not self._check_exchange_management_installed():
            self._install_exchange_management()
        self._courier.send("Interface", "Initialise", 1)
        if not self._check_microsoft_management_installed():
            self._install_microsoft_management()
        self._courier.send("Interface", "Initialise", 2)
    
    def start(self):
        """
        Start the Thread
        """
        self._logger.info("Starting O365 Process")
        while not self._process_event.is_set():
            message = self._courier.receive(timeout=-1)
            if message is not None:
                self._logger.debug(f"Received message: {message}")
                if message.type == "Initialise":
                    self.initialise_module()
                elif message.type == "Connect":
                    self._connect_exchange_management(message.content)
                elif message.type == "Disconnect":
                    self._disconnect_exchange_management()
                elif message.type == "Check Customization":
                    self._courier.send(message.sender, "Check Customization", self.check_exchange_customization())
                else:
                    self._logger.error(f"Unknown message type: {message.type}")
        self._shutdown_event.set()



if __name__ == '__main__':
    o = O365(None, None, None)
    o.initialise_module()
    o.connect_exchange_management("htiadmin@inselec.com.au")
    o.check_exchange_customization()
    o._disconnect_exchange_management()
    