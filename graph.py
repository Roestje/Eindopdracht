#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Import hier, import daar, import overal
from lxml import etree
import cgi, cgitb
import pymysql
import matplotlib
# Dit is de verplichte volgorde
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

    # Maak een legen lijst om te vullen
    x = []
    y = []

    # Loop door alle checks van een zekere Agent
    for rowChecks in mysqlChecksResult:
        check_timestamp = rowChecks["check_timestamp"]
        check_freeram = rowChecks["check_freeram"]
        check_cpupercentage = rowChecks["check_cpupercentage"]

        # Vul de X en Y as met datumtijden en percentages
        x.append(check_timestamp)
        y.append(check_cpupercentage)

    # Stel de grafiek in
    fig = plt
    fig.xlabel("Datumtijd", fontsize=14, color='red')
    fig.ylabel("% CPU belasting", fontsize=14, color='red')
    fig.plot(x,y)
    fig.gcf().autofmt_xdate()

    # Maak de grafiek en toon deze
    fig.savefig("/var/www/pythonserver/" + str(agent_id) + "_plt.png")
    print("<img src=\"" + str(agent_id) + "_plt.png\" />")
    # Afsluiten zodat de volgende gevuld kan worden
    fig.close()

print("<a href=\"index.py\">Kies andere agent</a>")
# Einde webpagina
print("</body>")
print("</html>")

mysqlConn.close()