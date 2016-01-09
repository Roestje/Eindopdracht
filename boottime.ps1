$Localization = New-Object System.Globalization.CultureInfo("en-US")

$LastBootUpTime = Get-WmiObject Win32_OperatingSystem | Select -Exp LastBootUpTime
$DateLastBootUpTime = [System.Management.ManagementDateTimeConverter]::ToDateTime($LastBootUpTime)

$date1 = Get-Date -Date "01/01/1970"
$date2 = Get-Date -Date $DateLastBootUpTime
$double = (New-TimeSpan -Start $date1 -End $date2).TotalSeconds

$double.ToString("", $Localization)