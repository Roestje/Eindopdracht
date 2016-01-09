#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Import hier, import daar, import overal
from lxml import etree
import cgi, cgitb

# Importeer XML
xml = "management_settings.xml"
tree = etree.parse(xml)

# Vul objecten uit XML file in variabelen
logfile = tree.xpath('/settings/logfile')[0].text

# Debuggen/foutmeldingen
cgitb.enable()

# Hier beginnen we de webpagina
print("Content-type: text/html;charset=utf-8\n")
print("<html>")
print("<head>")
print("<title>Management Python Eindopdracht</title>")
print("</head>")
print("<body>")
print("<h1>Eindopdracht Python: Nieuwe Agent</h1>")

# Nieuwe Agent
print("Let op, hier zit geen foutcontrole op. Dit is een extra service.<br /><br />")
print("<form action=\"addnewagent.py\" method=\"post\">")
print("Naam: <input type=\"text\" name=\"naam\" placeholder=\"Agent 007\" required/><br />")
print("Ip: <input type=\"text\" name=\"ip\" placeholder=\"192.168.220.137\" required/><br />")
print("Poort: <input type=\"text\" name=\"poort\" placeholder=\"Port\" value=\"8888\" required/><br />")
print("Wachtwoord: <input type=\"password\" name=\"wachtwoord\" placeholder=\"Wachtwoord\" required/><br />")
print("<input type=\"submit\"/>")
print("</form>")

print("<a href=\"index.py\">Annuleer, terug naar hoofdmenu</a>")
# Einde webpagina
print("</body>")
print("</html>")