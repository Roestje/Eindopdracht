#!/usr/bin/python
# -*- coding: UTF-8 -*-

import cgi, cgitb
from lxml import etree
import pymysql

# Importeer XML
xml = "management_settings.xml"
tree = etree.parse(xml)

# Vul objecten uit XML in variabel
allHosts = tree.xpath('/settings/host')
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

# Hier beginnen we de webpagina
print("Content-type: text/html;charset=utf-8\n")
print("<html>")
print("<head>")
print("<title>Management Python Eindopdracht</title>")
print("</head>")
print("<body>")
print("<h1>Eindopdracht Python</h1>")
print("Welkom, kies hieronder een agent uit om de gegevens op te vragen.<br /><br />")

# Live data
print("<h2>Live</h2>")
print("<form action=\"management.py\" method=\"get\">")

# We vragen alle agents op
mysqlCur.execute("SELECT agent_id, agent_name FROM agents")
mysqlResult = mysqlCur.fetchall()
print("<select name=\"agent\">")
print ("<option value=\"%s\">%s</option>" % (str(0), "Allemaal"))
for row in mysqlResult:
    print ("<option value=\"%s\">%s</option>" % (row["agent_id"], row["agent_name"]))
print("</select>")
print("<input type=\"submit\"/>")
print("</form>")


# Grafiekgeschiedenis
print("<h2>Grafiekgeschiedenis</h2>")
print("<form action=\"graph.py\" method=\"get\">")

# We vragen alle agents op
mysqlCur.execute("SELECT agent_id, agent_name FROM agents")
mysqlResult = mysqlCur.fetchall()
print("<select name=\"agent\">")
print ("<option value=\"%s\">%s</option>" % (str(0), "Allemaal"))
for row in mysqlResult:
    print ("<option value=\"%s\">%s</option>" % (row["agent_id"], row["agent_name"]))
print("</select>")
print("<input type=\"submit\"/>")
print("</form>")

# Tabelgeschiedenis
print("<h2>Tabelgeschiedenis</h2>")
print("<form action=\"table.py\" method=\"get\">")

# We vragen alle agents op
mysqlCur.execute("SELECT agent_id, agent_name FROM agents")
mysqlResult = mysqlCur.fetchall()
print("<select name=\"agent\">")
print ("<option value=\"%s\">%s</option>" % (str(0), "Allemaal"))
for row in mysqlResult:
    print ("<option value=\"%s\">%s</option>" % (row["agent_id"], row["agent_name"]))
print("</select>")
print("<input type=\"submit\"/>")
print("</form>")

print("<h2>Nieuwe Agent</h2>")
print("<a href=\"newagent.py\">Klik hier om een nieuwe agent toe te voegen</a>")

# Einde webpagina
print("</body>")
print("</html>")