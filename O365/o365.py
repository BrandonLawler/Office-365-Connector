from powershell import PowerShell
import multiprocessing


class O365:
    def __init__(self):
        self._powershell = PowerShell()
    
    def _check_exchange_management_installed(self):
        """
        Check if Exchange Management is installed
        """
        return self._powershell.run_command('Get-InstalledModule -Name ExchangeOnlineManagement')
    
    def _install_exchange_management(self):
        """
        Install Exchange Management
        """
        return self._powershell.run_command('Install-Module -Name ExchangeOnlineManagement')


if __name__ == '__main__':
    o = O365()
    print(o._check_exchange_management_installed())
    