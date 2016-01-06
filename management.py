import socket
import time
import datetime
import hashlib
from lxml import etree

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
    LogFile.write(Timestamp + LogLine + "\r")
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

        print(name)

        #welkomstbericht
        data = conn_readline(s)
        print(data)
        #wachtwoord melding
        data = conn_readline(s)
        print(data)
        #stuur wachtwoord mee
        wachtwoord = hashString(wachtwoord)
        s.send(bytes(wachtwoord, 'utf-8') + b"\r\n")
        data = conn_readline(s)
        print(data)

        #getPlatform
        s.send(b"getPlatform\r\n")
        platform = conn_readline(s)
        print(platform)

        #getBootTime
        s.send(b"getBootTime\r\n")
        bootTime = conn_readline(s)
        bootTime = datetime.datetime.fromtimestamp(float(bootTime)).strftime("%d-%m-%Y %H:%M:%S")
        print(bootTime)

        #getFreeRam
        s.send(b"getFreeRam\r\n")
        freeRam = round(float(conn_readline(s)))
        print(freeRam, "MB vrije RAM")

        #getCpuCount
        s.send(b"getCpuCount\r\n")
        cpuCount = conn_readline(s)
        print(cpuCount, "CPU's aanwezig")

        #getCpuPercentage
        s.send(b"getCpuPercentage\r\n")
        cpuPercentage = conn_readline(s)
        print(cpuPercentage, "%")

        #probeer de overkant te overtuigen dat de verbinding gesloten mag worden
        try:
            s.send(b"stop\r\n")
        #dit gaat sowieso mis als verbinding verbroken in dit script, dus vangen we dit af en sluiten deze socket netjes af voor hergebruik.
        except:
            s.close()

        WriteLog("Verbinding met " + hostname + " op poort " + str(port) + " gesloten")

        #ik moet de overkant de kans geven de verbinding te resetten. (t.b.v. testen 2x localhost)
        time.sleep(0.01)
    except:
        WriteLog("Verbinding maken met " + hostname + " op poort " + str(port) + " niet gelukt")



