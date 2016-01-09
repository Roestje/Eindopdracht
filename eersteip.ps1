$ipList = Get-NetIPAddress -AddressFamily IPv4 | select IPAddress | ForEach-Object {
    $ip = $_.IPAddress.ToString()
    if($ip.StartsWith("127") -Or $ip.StartsWith("169")) {

    } else {
        echo $ip
        break;
    }
}