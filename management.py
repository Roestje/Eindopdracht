#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Import hier, import daar, import overal
import socket
import datetime
import hashlib
from lxml import etree
import cgi, cgitb
import csv
import os
import pymysql

# Importeer XML
xml = "management_settings.xml"
tree = etree.parse(xml)

# Vul objecten uit XML file in variabelen
logfile = tree.xpath('/settings/logfile')[0].text
csvfileprefix = tree.xpath('/settings/csvfileprefix')[0].text
mysqlHost = tree.xpath('/settings/mysql/host')[0].text
mysqlPort = int(tree.xpath('/settings/mysql/port')[0].text)
mysqlUser = tree.xpath('/settings/mysql/user')[0].text
mysqlPassword = tree.xpath('/settings/mysql/password')[0].text
mysqlDatabase = tree.xpath('/settings/mysql/database')[0].text

# MySQL verbinding configureren
mysqlConn = pymysql.connect(host=mysqlHost, port=mysqlPort, user=mysqlUser, passwd=mysqlPassword, db=mysqlDatabase)
mysqlCur = mysqlConn.cursor(pymysql.cursors.DictCursor)

# Debuggen/foutmeldingen
cgitb.enable()
# Vul alles uit get in form
form = cgi.FieldStorage()

agent_id = form.getvalue("agent")

# Agent uit get is '0' als ze allemaal opgehaald worden, maar als er geen get is ook allemaal ophalen
if(agent_id == None or agent_id == '0'):
    # We vragen alle agents op
    mysqlCur.execute("SELECT * FROM agents")
    mysqlResult = mysqlCur.fetchall()
else:
    # We vragen alle agents op
    mysqlCur.execute("SELECT * FROM agents WHERE agent_id = %s", (agent_id))
    mysqlResult = mysqlCur.fetchall()

#curdir = "/var/www/pythonserver"
curdir = os.path.curdir
csvfile = curdir + "/" + csvfileprefix + "_" + str(datetime.datetime.now().strftime('%Y-%m-%d')) + ".csv"

# Maak een CSV dialect aan, ; in dit geval, Nederlands dus
csv.register_dialect('semicolon', delimiter=';')

# Controleer of bestand al bestaat, dit heeft te maken met titelrij
if os.path.isfile(csvfile):
    csvExists = 1
else:
    csvExists = 0

# Maak een CSV bestand aan, write
newCsv = open(csvfile, 'at', newline="")
csvWriter = csv.writer(newCsv, dialect='semicolon')

# Als het csv bestand niet bestaat, dan drukken we titelrij af
if csvExists == 0:
    csvWriter.writerow(('Tijdstip', 'Agentnaam', 'Platform', 'Utime (dagen)', 'RAM vrij (MB)', 'CPU aantal', 'CPU belasting (%)', 'IP'))

#logging functie
def WriteLog(LogLine):
    """
    Schrijft een regel in de log met timestamp ervoor
    :param LogLine: Regel die in de log moet
    """
    LogFile = open(logfile,'at')
    Timestamp = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S - ")
    LogFile.write(Timestamp + LogLine)
    LogFile.close()

def conn_readline(c):
    """
    Stukje code van meneer Van Staveren wat ervoor zorgt dat er geen lege regels gelezen worden.
    :param c: Open connectie van socket
    """
    s = "";
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

# Hier beginnen we de webpagina
print("Content-type: text/html;charset=utf-8\n")
print("<html>")
print("<head>")
print("<title>Management Python Eindopdracht</title>")
print("</head>")
print("<body>")
print("<h1>Eindopdracht Python</h1>")

# We lopen door alleHosts heen en gebruiken de info die is verkregen uit het XML bestand
# Om te verbinden met die hosts. Lukt dit niet, dan gaan we verder met de volgende.
for row in mysqlResult:
    id = int(row["agent_id"])
    name = row["agent_name"]
    hostname = row["agent_ip"]
    port = int(row["agent_port"])
    password = row["agent_password"]

    WriteLog("Probeer verbinding met " + hostname + " op poort " + str(port))

    connectionSucceed = 0

    print("<h2>" + name + "</h2>")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((hostname, port))
        connectionSucceed = 1
    except:
        WriteLog("Verbinding maken met " + hostname + " op poort " + str(port) + " niet gelukt")
        print("Verbinding maken met " + hostname + " op poort " + str(port) + " niet gelukt<br />")

    if connectionSucceed == 1:
        try:
            WriteLog("Verbinding maken met " + hostname + " op poort " + str(port) + " gelukt")

            #welkomstbericht
            data = conn_readline(s)
            #print(data)
            #wachtwoord melding
            data = conn_readline(s)
            #print(data)
            #stuur wachtwoord mee
            password = hashString(password)
            s.send(bytes(password, 'utf-8') + b"\n")
            data = conn_readline(s)
            #print(data)

            print("<table style=\"text-align:left\">")

            #getPlatform
            s.send(b"getPlatform\n")
            platform = conn_readline(s)
            print("<tr><th>Platform:</th><td>" + str(platform) + "</td></tr>")

            #getBootTime
            s.send(b"getBootTime\n")
            bootTime = conn_readline(s)
            if bootTime != "":
                #print("BootTime = " + str(bootTime))
                #print("Vergelijk met " + str(datetime.datetime.now().timestamp()))
                bootTime = datetime.datetime.now() - datetime.datetime.fromtimestamp(float(bootTime))
                bootDays = round(bootTime.total_seconds()/60/60/24)

                print("<tr><th>Aantal dagen up:</th><td>" + str(bootDays) + " dagen</td></tr>")

            #getFreeRam
            s.send(b"getFreeRam\n")
            freeRam = round(float(conn_readline(s)))
            if freeRam != "":
                print("<tr><th>Vrije RAM:</th><td>" + str(freeRam) + "MB</td></tr>")

            #getCpuCount
            s.send(b"getCpuCount\n")
            cpuCount = conn_readline(s)
            if cpuCount != "":
                print("<tr><th>Aantal CPU's:</th><td>" + str(cpuCount) + "CPU's</td></tr>")

            #getCpuPercentage
            s.send(b"getCpuPercentage\n")
            cpuPercentage = conn_readline(s)
            if cpuPercentage != "":
                print("<tr><th>CPU gebruik:</th><td>" + str(cpuPercentage) + "%</td></tr>")

            #getIp
            s.send(b"getIp\n")
            ip = conn_readline(s)
            if ip != "":
                print("<tr><th>IP Adres:</th><td>" + str(ip) + "</td></tr>")

            #getFreeSpace
            s.send(b"getFreeSpace\n")
            freeSpace = conn_readline(s)
            if freeSpace != "":
                print("<tr><th>Vrije ruimte C:</th><td>" + str(freeSpace) + "</td></tr>")

            print("</table>")

            csvWriter.writerow((datetime.datetime.now().strftime('%H:%M:%S'), name, platform, bootDays, freeRam, cpuCount, cpuPercentage, ip))

            timestamp = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            valueTuple = (int(id), timestamp, platform, bootDays, freeRam, cpuCount, cpuPercentage, ip)
            mysqlCur.execute('INSERT INTO checks (check_agent_id, check_timestamp, check_platform, check_uptime, check_freeram, check_cpucount, check_cpupercentage, check_ip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', valueTuple)
            mysqlConn.commit()

            # Probeer de overkant te overtuigen dat de verbinding gesloten mag worden
            try:
                s.send(b"stop\n")
            # Dit gaat sowieso mis als verbinding wordt verbroken in dit script, dus vangen we dit af en sluiten deze socket netjes af voor hergebruik.
            except:
                s.close()

            WriteLog("Verbinding met " + hostname + " op poort " + str(port) + " gesloten")

            #ik moet de overkant de kans geven de verbinding te resetten. (t.b.v. testen 2x localhost)
            #time.sleep(0.001)
        except:
            WriteLog("Er is een fout opgetreden tijdens het ophalen van de counters")

        s = None #even netjes opruimen voor de volgende

print("<a href=\"index.py\">Kies andere agent</a>")
# Einde webpagina
print("</body>")
print("</html>")

mysqlConn.close()

#csvfile sluiten
newCsv.close()