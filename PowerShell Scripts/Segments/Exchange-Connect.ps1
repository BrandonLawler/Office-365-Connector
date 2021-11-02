$userPrincipleName = $args[0]

Import-Module ExchangeOnlineManagement
Connect-ExchangeOnline -UserPrincipalName $userPrincipleName