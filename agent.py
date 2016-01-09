#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import socket
import sys
import datetime
import time
import psutil
import hashlib
from lxml import etree
import subprocess
import os

# Config uit xml halen
xml = 'agent_settings.xml'
tree = etree.parse(xml)

# Globale variabelen vullen met XML inhoud en desnoods casten naar juiste type
#HOST = tree.xpath('/settings/host/text()')[0]
HOST = "" # Moet leeg blijven, alle netwerkinterfaces luisteren
PORT = int(tree.xpath('/settings/port/text()')[0])
PASSWORD = tree.xpath('/settings/password/text()')[0]
LOGFILE = tree.xpath('/settings/logfile/text()')[0]

# Logging functie
def WriteLog(LogLine):
    """
    Schrijft een regel in de log met timestamp ervoor
    :param LogLine: Regel die in de log moet
    """
    LogFile = open(LOGFILE,'a')
    Timestamp = time.strftime("%d-%m-%Y %H:%M:%S - ")
    LogFile.write(Timestamp + LogLine + "\r")
    LogFile.close()

def conn_readline(c):
    """
    Stukje code van meneer Van Staveren wat ervoor zorgt dat er geen lege regels gelezen worden.
    :param c: Open connectie van socket, waar we op luisteren
    """
    s = ""
    while not s.endswith('\n'):
        data = c.recv(2048)
        s += data.decode('utf-8')
    return s.rstrip()

def hashString(s):
    """
    Deze functie hasht een string en geeft deze terug
    :param s: String die een MD5 hash krijgt
    :return: De gehashde string
    """
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
VerbindingSuccess = 0

while VerbindingSuccess == 0:
    # Zolang er geen verbinding succesvol is, proberen we PORT te gebruiken. Deze is in een XML config opgenomen,
    # maar kan bij een mislukte verbinding handmatig aangepast worden d.m.v. input.
    try:
        s.bind((HOST, PORT))
        VerbindingSuccess = 1
        WriteLog("Socket gestart op poort " + str(PORT))
    except:
        WriteLog("Socket kon niet gestart worden op poort" + str(PORT))
        PORT = int(input("Poort " + str(PORT) + " in gebruik, geef een andere poort op"))

s.listen(10)
print('> Socket luistert op poort:',PORT)

while 1==1:
    # Wacht op connecties (blocking)
    conn, addr = s.accept()

    # Er is een client verbonden met de server
    print('> Verbonden met ' + addr[0] + ':' + str(addr[1]))
    WriteLog('Verbonden met ' + addr[0] + ':' + str(addr[1]))

    conn.sendall(b'CLIENT CONNECTED\r\n')

    data = ""
    wachtwoord = hashString(PASSWORD)
    poging = 0
    authenticatie = 0

    try:
        while authenticatie == 0 and poging <= 3:
            # Zolang er geen authenticatie plaatsvond en poging nog onder of gelijk aan 3 is, wordt het password gevraagd.
            conn.sendall(b'PASSWORD REQUIRED\r\n')
            data = conn_readline(conn)

            if data == wachtwoord and authenticatie == 0:
                # Login succesvol
                WriteLog("Er werd succesvol ingelogd door management")
                authenticatie = 1
                # De server meldt zich aan de client
                conn.sendall(b'PASSWORD OK COMMAND LINE OPEN\r\n')
            else:
                # Login niet succesvol
                conn.sendall(b'PASS WRONG')
                print("w:", wachtwoord, "d:", data)
                conn.sendall(b'\r\n')
                poging += 1
                WriteLog("Wachtwoord poging " + str(poging) + " van 3, was foutief")

        if poging > 3:
            WriteLog("Er zijn meer dan 3 pogingen geweest voor het wachtwoord, verbinding verbroken")
    except:
        WriteLog("Verbinding verbrak door onbekende reden")
        print("Verbinding verbrak door onbekende reden")

    data = ""
    try:
        while authenticatie == 1:
            # Zolang er een geldige authenticatie is, luisteren we naar de commando's van management.
            data = conn_readline(conn)
            platform = sys.platform

            #hieronder eerst een lijst met gelijke implementaties
            if data == "stop":
                # op verzoek van het managementscript verbreken we de verbinding en maken we de lijn weer vrij voor een volgende keer
                WriteLog("Verbinding werd netjes verbroken op verzoek van management\r")
                break # uit de while duiken
            elif data == "getPlatform":
                # wat voor OS is het?
                conn.sendall(str.encode(platform))
                WriteLog("Commando getPlatform gevraagd en " + platform + " geantwoord")
            elif data == "getIpDict":
                # hieronder vragen we een dictionary van interfaces op
                ifdict = psutil.net_if_addrs()
                conn.sendall(str.encode(str(ifdict)))
                WriteLog("Commando getIpDict gevraagd en " + str(ifdict) + " geantwoord")
            elif data == "getCpuPercentage":
                cpuPercentage = psutil.cpu_percent()
                conn.sendall(str.encode(str(cpuPercentage)))
                WriteLog("Commando getCpuPercentage gevraagd en " + str(cpuPercentage) + " geantwoord")
            elif data == "getCpuCount":
                cpuCount = psutil.cpu_count()
                conn.sendall(str.encode(str(cpuCount)))
                WriteLog("Commando getCpuCount gevraagd en " + str(cpuCount) + " geantwoord")
            else: # Dan moet het haast wel een commando zijn met specifieke implementatie
                if platform.startswith('win'):
                    curdir = os.path.dirname(os.path.abspath(__file__))
                    if data == "getBootTime":
                        p=subprocess.Popen(['powershell.exe',    # Altijd gelijk of volledig pad naar powershell.exe
                        '-ExecutionPolicy', 'Unrestricted',  # Override current Execution Policy
                        curdir + '\\boottime.ps1'],  # Naam van en pad naar je PowerShell script
                        stdout=subprocess.PIPE)                  # Zorg ervoor dat je de STDOUT kan opvragen.
                        bootTime = p.stdout.read().rstrip().lstrip().decode('utf-8')[:-4] # De stdout met strips en decoder om het een leesbaar getal te maken

                        conn.sendall(str.encode(str(bootTime)))
                        WriteLog("Commando getBootTime met powershell gevraagd en " + str(bootTime) + " geantwoord")
                    elif data == "getFreeRam":
                        p=subprocess.Popen(['powershell.exe',    # Altijd gelijk of volledig pad naar powershell.exe
                        '-ExecutionPolicy', 'Unrestricted',  # Override current Execution Policy
                        curdir + '\\vrijgeheugen.ps1'],  # Naam van en pad naar je PowerShell script
                        stdout=subprocess.PIPE)                  # Zorg ervoor dat je de STDOUT kan opvragen.
                        output = p.stdout.read().rstrip().lstrip().decode('utf-8') # De stdout met strips en decoder om het een leesbaar getal te maken
                        freeram = int(output) / 1024 #zet het om naar MB

                        conn.sendall(str.encode(str(freeram)))
                        WriteLog("Commando getFreeRam met PowerShell gevraagd en " + str(freeram) + " geantwoord")
                    elif data == "getIp":
                        p=subprocess.Popen(['powershell.exe',    # Altijd gelijk of volledig pad naar powershell.exe
                        '-ExecutionPolicy', 'Unrestricted',  # Override current Execution Policy
                        curdir + '\\eersteip.ps1'],  # Naam van en pad naar je PowerShell script
                        stdout=subprocess.PIPE)                  # Zorg ervoor dat je de STDOUT kan opvragen.
                        output = p.stdout.read().rstrip().lstrip().decode('utf-8') # De stdout met strips en decoder om het een leesbaar getal te maken
                        ip = str(output)

                        conn.sendall(str.encode(ip))
                        WriteLog("Commando getIp met PowerShell gevraagd en " + ip + " geantwoord")
                    elif data == "getFreeSpace":
                        p=subprocess.Popen(['powershell.exe',    # Altijd gelijk of volledig pad naar powershell.exe
                        '-ExecutionPolicy', 'Unrestricted',  # Override current Execution Policy
                        curdir + '\\vrijeruimtec.ps1'],  # Naam van en pad naar je PowerShell script
                        stdout=subprocess.PIPE)                  # Zorg ervoor dat je de STDOUT kan opvragen.
                        output = p.stdout.read().rstrip().lstrip().decode('utf-8') # De stdout met strips en decoder om het een leesbaar getal te maken
                        freeSpace = round(int(output) / 1024 / 1024) #zet het om naar MB

                        conn.sendall(str.encode(str(freeSpace) + " MB"))
                        WriteLog("Commando getFreeSpace met PowerShell gevraagd en " + str(freeSpace) + " geantwoord")


                if platform.startswith('linux'):
                    if data == "getBootTime":
                        # Wanneer was deze machine opgestart?
                        bootTime = psutil.boot_time()
                        conn.sendall(str.encode(str(bootTime)))
                        WriteLog("Commando getBootTime gevraagd en " + str(bootTime) + " geantwoord")
                    elif data == "getFreeRam":
                        # vraag alle gegevens over RAM op
                        vmem = psutil.virtual_memory()
                        # filter vrije ram eruit en zet het om naar MB
                        freeram = vmem.free / 1024 / 1024
                        conn.sendall(str.encode(str(freeram)))
                        WriteLog("Commando getFreeRam gevraagd en " + str(freeram) + " geantwoord")
                    elif data == "getIp":
                        ipAddress = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s1.connect(('8.8.8.8', 80)), s1.getsockname()[0], s1.close()) for s1 in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

                        conn.sendall(str.encode(str(ipAddress)))
                        WriteLog("Commando getIp gevraagd en " + str(ipAddress) + " geantwoord")
                    elif data == "getFreeSpace":
                        freeSpace = "Niet voor Linux"

                        conn.sendall(str.encode(str(freeSpace)))
                        WriteLog("Commando getFreeSpace gevraagd en " + str(freeSpace) + " geantwoord")


            conn.sendall(b'\r\n')
    except:
        WriteLog("Verbinding verbrak om onbekende reden")
        print("Verbinding verbrak om onbekende reden")

    conn.close()

s.close()