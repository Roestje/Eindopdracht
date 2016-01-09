#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Import hier, import daar, import overal
import datetime
from lxml import etree
import cgi, cgitb
import pymysql

# Importeer XML
xml = "management_settings.xml"
tree = etree.parse(xml)

# Vul objecten uit XML file in variabelen
logfile = tree.xpath('/settings/logfile')[0].text
mysqlHost = tree.xpath('/settings/mysql/host')[0].text
mysqlPort = int(tree.xpath('/settings/mysql/port')[0].text)
mysqlUser = tree.xpath('/settings/mysql/user')[0].text
mysqlPassword = tree.xpath('/settings/mysql/password')[0].text
mysqlDatabase = tree.xpath('/settings/mysql/database')[0].text

# MySQL verbinding configureren
mysqlConn = pymysql.connect(host=mysqlHost, port=mysqlPort, user=mysqlUser, passwd=mysqlPassword, db=mysqlDatabase)
mysqlCur = mysqlConn.cursor(pymysql.cursors.DictCursor)

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

# Debuggen/foutmeldingen
cgitb.enable()
# Vul alles uit get in form
form = cgi.FieldStorage()

# Alle gegevens uit form ophalen
agent_name = form.getvalue("naam")
agent_ip = form.getvalue("ip")
agent_port = form.getvalue("poort")
agent_password = form.getvalue("wachtwoord")

# En naar database wegschrijven
valueTuple = (agent_name, agent_ip, agent_port, agent_password)
mysqlCur.execute('INSERT INTO agents (agent_name, agent_ip, agent_port, agent_password) VALUES (%s, %s, %s, %s)', valueTuple)
mysqlConn.commit()

# Hier beginnen we de webpagina
print("Content-type: text/html;charset=utf-8\n")
print("<html>")
print("<head>")
print("<title>Management Python Eindopdracht</title>")
print("</head>")
print("<body>")
print("<h1>Eindopdracht Python: Nieuwe Agent</h1>")

print("Agent " + agent_name + "toegevoegd aan database.<br />")

print("<a href=\"index.py\">Ga terug naar hoofdmenu</a>")
# Einde webpagina
print("</body>")
print("</html>")

mysqlConn.close()