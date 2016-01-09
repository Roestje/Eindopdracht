#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Import hier, import daar, import overal
from lxml import etree
import cgi, cgitb
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

# Hier beginnen we de webpagina
print("Content-type: text/html;charset=utf-8\n")
print("<html>")
print("<head>")
print("<title>Management Python Eindopdracht</title>")
print("</head>")
print("<body>")
print("<h1>Eindopdracht Python: Grafiekjes</h1>")

# We lopen door alleHosts heen en gebruiken de info die is verkregen uit de database
for row in mysqlResult:
    agent_id = int(row["agent_id"])
    name = row["agent_name"]

    print("<h2>" + name + "</h2>")

    # We vragen alle checks van een zekere agent op
    mysqlCur.execute("SELECT * FROM checks WHERE check_agent_id = %s", (agent_id))
    mysqlChecksResult = mysqlCur.fetchall()

    print("<table style=\"text-align: left;\">")
    print("<tr style=\"border: black solid 1px;\"><th>Datumtijd</th><th>Platform</th><th>Uptime in dagen</th><th>Vrije RAM</th><th>Aantal CPU's</th><th>CPU belasting (%)</th><th>IP Adres</th></tr>")

    # Loop door alle checks van een zekere Agent
    for rowChecks in mysqlChecksResult:
        check_timestamp = rowChecks["check_timestamp"]
        check_platform = rowChecks["check_platform"]
        check_uptime = rowChecks["check_uptime"]
        check_freeram = rowChecks["check_freeram"]
        check_cpucount = rowChecks["check_cpucount"]
        check_cpupercentage = rowChecks["check_cpupercentage"]
        check_ip = rowChecks["check_ip"]

        print('<tr style=\"border: black solid 1px;\"><td>%s</td><td>%s</td><td>%s dagen</td><td>%s MB</td><td>%s CPU\'s</td><td>%s %%</td><td>%s</td></tr>'%(check_timestamp, check_platform, check_uptime, check_freeram, check_cpucount, check_cpupercentage, check_ip))
    print("</table>")


print("<a href=\"index.py\">Kies andere agent</a>")
# Einde webpagina
print("</body>")
print("</html>")

mysqlConn.close()