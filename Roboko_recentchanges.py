# -*- coding: utf-8 -*-

import time
import re
import irclib
import httplib
import json

import Roboko_utils as rbk_utils

IGNORED_NAMESPACE = [
    "Discussion",
    "Utilisateur",
    "Utilisatrice",
    "Wikipédia",
    "Fichier",
    "Sujet",
    "MediaWiki",
    "Modèle",
    "Aide",
    "Catégorie",
    "Portail",
    "Projet",
    "Référence",
    "Module",
    "Spécial",
    "Discussion utilisateur",
    "Discussion utilisatrice",
    "Discussion Wikipédia",
    "Discussion fichier",
    "Discussion MediaWiki",
    "Discussion modèle",
    "Discussion aide",
    "Discussion catégorie",
    "Discussion Portail",
    "Discussion Projet",
    "Discussion Référence",
    "Discussion module"
]


r_title = re.compile("^\00314\[\[\00307(.+)\00314\]\]")
r_author = re.compile("\*\003 \00303(.+)\003 \0035\*")
r_summary = re.compile("\0035\*\003 \([+-][0-9]+\) \00310(.*)\003")
r_oldid = re.compile("diff=([0-9]+)")
r_prev_oldid = re.compile("oldid=([0-9]+)")
r_newpage = re.compile("\]\]\0034 !?N")
r_move = re.compile("moved \[\[\00302(.+)\00310\]\] to \[\[([^\]]+)\]\](.+)*\003")
r_type = [
	re.compile(ur"\{\{Infobox Animation et bande dessinée asiatiques/Entête(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*type *=([^\}\|]*)"),
	re.compile(ur"\{\{Infobox Animation et bande dessinée asiatiques/Livre(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*public_cible *=([^\}\|]*)")
]
r_abda_portal = re.compile(u"\{\{[Pp]ortail.+([Aa]nimation et bande dessinée asiatiques|[Aa][Bb][Dd][Aa]).*\}\}")

conn = httplib.HTTPSConnection("fr.wikipedia.org")
irc_rcv = None
irc_send = None


def init(mainirc, pseudo):
	global irc_rcv, irc_send
	irc_send = mainirc
	irc_rcv = irclib.IRC()
	server = irc_rcv.server()
	server.connect("irc.wikimedia.org", 6667, pseudo, ssl=False)
	server.join("#fr.wikipedia")
	irc_rcv.add_global_handler("pubmsg", analyse, -10)





def isPartOfProject(title, project, retry=0):
	global conn
	try:
		conn.request("GET", u"/w/api.php?action=query&rawcontinue&prop=categories&format=json&titles="+title.replace(" ", "_"))
		cats = json.loads(conn.getresponse().read())["query"]["pages"].itervalues().next()
		if "categories" in cats:
			cats = cats["categories"]
			for item in cats:
				if item["title"] == "Catégorie:Portail:"+project+"/Articles liés":
					return True
					break
	except:
		if retry < 4:
			conn = httplib.HTTPSConnection("fr.wikipedia.org")
			return isPartOfProject(title, project, retry+1)
		else:
			print "\n5 HTTP errors had occured in isPartOfProject\n"
	return False


def isOnRevision(oldid, regex, retry=0):
	global conn
	try:
		conn.request("GET", u"/w/api.php?action=query&prop=revisions&rvprop=content&format=json&revids="+oldid)
		content = json.loads(conn.getresponse().read())["query"]["pages"].itervalues().next()["revisions"][0]["*"]
		if regex.search(content):
			return True
	except:
		if retry < 4:
			conn = httplib.HTTPSConnection("fr.wikipedia.org")
			return isOnRevision(oldid, regex, retry+1)
		else:
			print "\n5 HTTP errors had occured in isOnRevision\n"
			return None
	return False

def isAutopatrolled(user, retry=0):
	global conn
	if rbk_utils.isIp(user):
		return False
	conn.request("GET", u"/w/api.php?format=json&action=query&list=users&usprop=groups&ususers="+user.replace(" ", "_"))
	try:
		if "autopatrolled" in json.loads(conn.getresponse().read())["query"]["users"][0]["groups"]:
			return True
	except:
		if retry < 4:
			conn = httplib.HTTPSConnection("fr.wikipedia.org")
			return isAutopatrolled(user, retry+1)
		else:
			print "\n5 HTTP errors had occured in isAutopatrolled\n"
	return False

def hasTypeChanged(title, oldid, prev_oldid, retry=0):
	global conn
	try:
		conn.request("GET", u"/w/api.php?action=query&prop=revisions&rvprop=content&format=json&revids="+prev_oldid+"|"+oldid)
		revs = json.loads(conn.getresponse().read())["query"]["pages"].itervalues().next()["revisions"]
		for regex in r_type:
			oldtype = regex.findall(revs[0]["*"])
			newtype = regex.findall(revs[1]["*"])
			if oldtype != [] and newtype != []:
				oldtype = oldtype[0].replace("\n", "").strip().lower()
				newtype = newtype[0].replace("\n", "").strip().lower()
				if oldtype != newtype:
					return (True, oldtype, newtype)
	except:
		if retry < 4:
			conn = httplib.HTTPSConnection("fr.wikipedia.org")
			return hasTypeChanged(title, oldid, prev_oldid, retry+1)
		else:
			print "\n5 HTTP errors had occured in hasTypeChanged\n"
	return (False, "", "")


def analyse(serv, ev, retry=0):
	global conn, irc_send
	message = ev.arguments()[0]
	title = r_title.findall(message)[0]
	N = " "
	P = " "
	oldid = "0"
	print message;

	#Pour les articles, et les articles uniquement
	if not title.split(":")[0] in IGNORED_NAMESPACE:
		author = r_author.findall(message)[0]
		if r_newpage.search(message):
			N = "N"
			oldid = r_prev_oldid.findall(message)[0]
		else:
			oldid = r_oldid.findall(message)[0]
		onrevision = isOnRevision(oldid, r_abda_portal)
		if onrevision == True: #isPartOfProject(title, "Animation et bande dessinée asiatiques"):
			P = "P"
		elif onrevision == False:
			P = "_"

		#Informe des nouveaux articles
		if P == "P" and N == "N":
			irc_send.send(irc_send.chan, u"\00313\002Nouvel article\002\003 : [[\00307"+ title + u"\003]] – \00310" + rbk_utils.article_link(title.encode('utf-8')) + "\003")
		
		if P == "P" and N != "N":
			prev_oldid = r_prev_oldid.findall(message)[0]
			#Informe des changements de type
			if not isAutopatrolled(author):
				(changed, oldtype, newtype) = hasTypeChanged(title, oldid, prev_oldid)
				if changed:
					irc_send.send(irc_send.chan, author+u" a modifié le type de [["+title+u"]], de \""+oldtype+u"\" à \""+newtype+u"\" — https://fr.wikipedia.org/w/index.php?diff="+oldid)
					N = "C"
			#Informe des nouveaux portails abda posés
			if isOnRevision(prev_oldid, r_abda_portal) == False:
				irc_send.send(irc_send.chan, author+u" a ajouté le portail abda à l'article [["+title+u"]] — https://fr.wikipedia.org/w/index.php?diff="+oldid)
				P = "A"
		elif P == "_" and N != "N":
			prev_oldid = r_prev_oldid.findall(message)[0]
			#Informe des portails abda retirés
			if isOnRevision(prev_oldid, r_abda_portal):
				irc_send.send(irc_send.chan, author+u" a retiré le portail abda de l'article [["+title+u"]] — https://fr.wikipedia.org/w/index.php?diff="+oldid)
				P = "X"

		print N + P + "  " + title + " by #" + author + "#"

	#Informe des articles abda déplacés
	elif title == "Spécial:Log/move":
		movedata = r_move.findall(message)[0]
		oldtitle = movedata[0]
		newtitle = movedata[1]
		if len(movedata) > 2:
			summary = movedata[2]
		else:
			summary = ""
		if not(oldtitle.split(":")[0] in IGNORED_NAMESPACE) or not(newtitle.split(":")[0] in IGNORED_NAMESPACE):
			author = r_author.findall(message)[0]
			if isPartOfProject(newtitle, "Animation et bande dessinée asiatiques"):
				P = "P"
				irc_send.send(irc_send.chan, u"\00313\002Article renommé\002\003 : la page [[\00307"+ oldtitle + u"\003]] a été déplacé vers [[\00307"+ newtitle + u"\003]] par \00303"+author+u"\003" + summary + u" – \00310" + rbk_utils.article_link(newtitle.encode('utf-8')) + "\003")
			print "M" + P + "  " + author + " a déplacé la page [[" + oldtitle + "]] vers [[" + newtitle + "]]"

	#Informe des nouveaux messages sur le manga café
	elif title == "Discussion Projet:Animation et bande dessinée asiatiques":
		author = r_author.findall(message)[0]
		oldid = r_oldid.findall(message)[0]
		summary = r_summary.findall(message)
		if summary != []:
			summary = summary[0]
		else:
			summary = ""
		print "DP  " + author + " a déposé un nouveau message sur le Manga Café : " + summary
		irc_send.send(irc_send.chan, u"\00313\002Nouveau message sur le Manga café\002\003 par \00303"+author+u"\003 – \00310https://fr.wikipedia.org/w/index.php?diff="+oldid+" – "+summary)
			

def process_once():
	irc_rcv.process_once(0.2)
