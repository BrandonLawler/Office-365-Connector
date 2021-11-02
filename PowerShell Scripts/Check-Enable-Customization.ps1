$userPrincipleName = $args[0]
$

Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline -UserPrincipalName $userPrincipleName

if (Get-OrganizationConfig | IsDehydrated == $true) {
    try {
        Enable-OrganizationCustomization
        $activated = $true
    } catch {
        $activated = $false
    }
} else {
    $activated = $true
}

Disconnect-ExchangeOnline
return $activated