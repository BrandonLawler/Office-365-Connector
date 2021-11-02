if (Get-OrganizationConfig | IsDehydrated == $true) {
    return $false
}
return $true