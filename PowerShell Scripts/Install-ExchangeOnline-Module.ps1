
if (Get-Module -ListAvailable -Name ExchangeOnlineManagement) {
    return $true
} else {
    try {
        Install-Module -Name ExchangeOnlineManagement
        return $true
    } catch {
        return $false
    }
}
return $false
