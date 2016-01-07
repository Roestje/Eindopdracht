#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Hier beginnen we de webpagina
print("Content-type: text/html;charset=utf-8\n")

import socket
import time
import datetime
import hashlib
from lxml import etree
import cgi, cgitb
cgitb.enable()

print("<html>")
print("<head>")
print("<title>Management Python Eindopdracht</title>")
print("</head>")
print("<body>")

# Importeer XML
xml = "management_settings.xml"
tree = etree.parse(xml)

# Vul objecten in variabel
alleHosts = tree.xpath('/settings/host')
logfile = tree.xpath('/settings/logfile')[0].text

#logging functie
def WriteLog(LogLine):
    LogFile = open(logfile,'a')
    Timestamp = time.strftime("%d-%m-%Y %H:%M:%S - ")
    LogFile.write(Timestamp + LogLine) # \r stond hier ook.
    LogFile.close()

def conn_readline(c):
    s = "";
    while not s.endswith('\n'):
        data = c.recv(1024)
        s += data.decode('ascii')
    return s.rstrip()

def hashString(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()

for host in alleHosts:
    name = host[0].text
    hostname = host[1].text
    port = int(host[2].text)
    wachtwoord = host[3].text

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((hostname, port))

        WriteLog("Verbinding maken met " + hostname + " op poort " + str(port) + " gelukt")

        print("<h1>Eindopdracht Python</h1>")
        print("<h2>" + name + "</h2>")

        #welkomstbericht
        data = conn_readline(s)
        #print(data)
        #wachtwoord melding
        data = conn_readline(s)
        #print(data)
        #stuur wachtwoord mee
        wachtwoord = hashString(wachtwoord)
        s.send(bytes(wachtwoord, 'utf-8') + b"\n")
        data = conn_readline(s)
        #print(data)

        print("<table>")

        #getPlatform
        s.send(b"getPlatform\n")
        platform = conn_readline(s)
        print("<tr><th>Platform:</th><td>" + str(platform) + "</td></tr>")

        #getBootTime
        #s.send(b"getBootTime\n")
        #bootTime = conn_readline(s)
        #bootTime = datetime.datetime.fromtimestamp(float(bootTime)).strftime("%d-%m-%Y %H:%M:%S")
        #print(bootTime)

        #getFreeRam
        s.send(b"getFreeRam\n")
        freeRam = round(float(conn_readline(s)))
        print("<tr><th>Vrije RAM:</th><td>" + str(freeRam) + "MB</td></tr>")

        #getCpuCount
        s.send(b"getCpuCount\n")
        cpuCount = conn_readline(s)
        print("<tr><th>Aantal CPU's:</th><td>" + str(cpuCount) + "CPU's</td></tr>")

        #getCpuPercentage
        s.send(b"getCpuPercentage\n")
        cpuPercentage = conn_readline(s)
        print("<tr><th>CPU gebruik:</th><td>" + str(cpuPercentage) + "%</td></tr>")

        print("</table>")

        #probeer de overkant te overtuigen dat de verbinding gesloten mag worden
        try:
            s.send(b"stop\n")
        #dit gaat sowieso mis als verbinding verbroken in dit script, dus vangen we dit af en sluiten deze socket netjes af voor hergebruik.
        except:
            s.close()

        WriteLog("Verbinding met " + hostname + " op poort " + str(port) + " gesloten")

        #ik moet de overkant de kans geven de verbinding te resetten. (t.b.v. testen 2x localhost)
        time.sleep(0.01)
    except:
        WriteLog("Verbinding maken met " + hostname + " op poort " + str(port) + " niet gelukt")

# Einde webpagina
print("</body>")
print("</html>")