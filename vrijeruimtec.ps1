get-WmiObject win32_logicaldisk -Filter "DeviceID='C:'" | select FreeSpace | ft -hidetableheaders