#!/usr/bin/python
# -*- coding: utf-8 -*-
#Autor: Antoine Lamielle "0x010C"
#Date: 19 february 2015
#License: GNU GPL v3

import httplib;
import time;
import calendar;
import os;
import sys;
from feedparser import parse;
import irclib;
import ircbot;
import re;
import unicodedata;
import urllib;

#Paramètres
version = "1.17"
chan = "";
pseudo = "";
password = "";
server = "verne.freenode.net";
port = 6667;
converttable = [];

wait = 300;
cat = "https://fr.wikipedia.org/w/api.php?hidebots=1&days=7&limit=50&target=Catégorie:Portail:Animation+et+bande+dessinée+asiatiques/Articles+liés&hidewikidata=1&action=feedrecentchanges&feedformat=atom";
page = "https://fr.wikipedia.org/w/index.php?title=Discussion_Projet:Animation_et_bande_dessin%C3%A9e_asiatiques&feed=atom&action=history";

old_timestamp1 = calendar.timegm(time.gmtime());
old_timestamp2 = calendar.timegm(time.gmtime());


# Boucle principale + Gestion de la lecture et de l'écriture IRC
class mybot(ircbot.SingleServerIRCBot):
	def __init__(self):
		ircbot.SingleServerIRCBot.__init__(self, [(server, port)],pseudo, "Roboko v"+version);

	def on_welcome(self, serv, ev):
		self.saveServ = serv;
		if password != "":
			self.send("nickserv", "identify " + password);
			time.sleep(10);
		serv.join(chan);
		self.checker();

	def on_privnotice(self, serv, ev):
		print "#" + irclib.nm_to_n(ev.source()) + "# --> " + ev.arguments()[0];

	def on_pubmsg(self, serv, ev):
		author = irclib.nm_to_n(ev.source());
		canal = ev.target();
		message = ev.arguments()[0];
		self.command(author, canal, message);

	def on_action(self, serv, ev):
		author = irclib.nm_to_n(ev.source());
		canal = ev.target();
		message = ev.arguments()[0];
		self.command(author, canal, message);

	def send(self, to, message):
		try:
			self.saveServ.privmsg(to, message);
		except:
			print u"except";

	def act(self, to, message):
		try:
			self.saveServ.action(to, message);
		except:
			print u"except";

	def command(self, author, canal, message):
		print author + " --> " + message;
		if re.search("^!help", message):
			self.send(author, "Roboko, bot irc pour le chan du Projet:Animation et bande dessinée asiatiques sur la Wikipédia francophone (##abda)");
			time.sleep(1);
			self.send(author, " ");
			self.send(author, "Commandes disponibles :");
			self.send(author, "!help : affiche ce message d'aide");
			self.send(author, "!jisho : tranduit et transcrit un mot japonais");
			self.send(author, "[[lien interne WP]] : traduit un lien interne en url");
			self.send(author, "Annonce les nouveaux articles du Portail:ABDA");
			self.send(author, "Annonce les nouveaux sujets sur le Manga café");
			time.sleep(1);
			self.send(author, " ");
			self.send(author, "Roboko v"+version+", développé par 0x010C en python2.7 d'après les idées de Thibaut120094");
		if re.search("\[\[.+\]\]", message):
			print article_link(re.split("\[\[(.+)\]\]", message)[1].strip());
			self.send(canal, article_link(re.split("\[\[(.+)\]\]", message)[1].strip()));
		if re.search("^!jisho .+", message):
			self.send(canal, self.jisho(message[7:]));
		

	def checker(self):
		print "### Checker";
		self.check_new_article(cat);
		self.check_new_section(page);
		self.saveServ.execute_delayed(wait, self.checker);


	# Les checkers
	def check_new_article(self, cat_link):
		global old_timestamp1;
		timestamp1 = calendar.timegm(time.gmtime());
		entries = get_new_entries(cat_link, old_timestamp1);
		for item in entries:
			if re.search("\n<p><b>Nouvelle page</b></p>", item.summary):
				tmp = u"– Nouvel article : [["+ item.title + u"]] – " + article_link(item.title.encode('utf-8'));
				self.act(chan, tmp.encode('utf-8'));
				time.sleep(2);
#			else:
#				if isIp(item.author):
#					tmp = u"- Modification de [["+ item.title + u"]] par " + item.author + u" - " + article_link(item.title.encode('utf-8'));
#					print tmp;
#					self.act(chan, tmp.encode('utf-8'));
#					time.sleep(2);
		old_timestamp1 = timestamp1;
		
	def check_new_section(self, page_link):
		global old_timestamp2;
		timestamp2 = calendar.timegm(time.gmtime());
		entries = get_new_entries(page_link, old_timestamp2);
		conn = httplib.HTTPSConnection("fr.wikipedia.org");
		for item in entries:
			conn.request("GET", item.id[24:]);
			print item.id[24:];
			result = re.findall('<td class="diff-addedline"><div>==(.+)==.*</div></td>', conn.getresponse().read());
			if len(result) > 0:
				if result[0][0] != '=':
					result[0] = result[0].strip();
					tmp = u"– Nouveau sujet sur le Manga Café par "+item.author+u" : https://fr.wikipedia.org/wiki/Discussion_Projet:Animation_et_bande_dessinée_asiatiques#"+urllib.quote_plus(result[0].replace(" ", "_"));
					print tmp.encode('utf-8');
					self.act(chan, tmp.encode('utf-8'));
					time.sleep(2);
		old_timestamp2 = timestamp2;

	def jisho(self, message):
		conn = httplib.HTTPConnection("tangorin.com");
		conn.request("GET", "/general/"+urllib.quote_plus(message));
		result = re.findall('<div class="entry"><a class="btn btn-link entry-menu" onclick="entryMenu\(this,\{\n([\s\S]+)</div>', conn.getresponse().read());
		if len(result) > 0:
			result = result[0].split("\">")[0].split("\n")[2:6];
			for line in result:
				line = line.split(":")[1];
			kanji = re.findall("'(.*)'",result[0])[0];
			kana = re.findall("'(.*)'",result[1])[0].split("・")[0];
			trad = re.findall("'(.*)'",result[3])[0].replace("<ol>", "").replace("</ol>", "").replace("</li><li>", " - ").replace("<li>", "").replace("</li>", "");

			output = kanji + "[" + kana + ", " + kana2romaji(kana) + "] --> " + trad;
			return output.encode('utf-8');
		else:
			trad = kana2romaji(message);
			if len(trad) > 0:
				return "Introuvable, tentative de transcription : " + trad;
			else:
				return "Introuvable";



# Gestion du temps
def timestampisation(date):
	return time.mktime(time.strptime(date,"%Y-%m-%dT%H:%M:%SZ"));


# Recuperation de feed rss
def get_entries(link):
	feed = parse(link);
	return feed['entries'];

def get_new_entries(link, old_timestamp):
	feed = get_entries(link);
	entries = [];
	for item in feed:
		if int(timestampisation(item.updated)) > int(old_timestamp):
			entries.append(item);
	return entries;

# Divers
def article_link(link):
	return "https://fr.wikipedia.org/wiki/" + urllib.quote_plus(link.replace(" ", "_"));

def isIp(name):
	if re.search("^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$", name):
		return True;
	else:
		if re.search("^[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}$", name):
			return True;
		else:
			return False;

# Args
def parse_config_file():
	global chan;
	global pseudo;
	global password;
	if(os.path.isfile("Roboko.conf") == False):
		return;
	fichier = open("Roboko.conf", "r");
	contenu = fichier.read();
	fichier.close();
	for line in contenu.split("\n"):
		if re.search("^[Cc]han:", line):
			chan = line[5:];
		if re.search("^[Pp]seudo:", line):
			pseudo = line[7:];
		if re.search("^[Pp]assword:", line):
			password = line[9:];

def get_args():
	global chan;
	global pseudo;
	global password;
	parse_config_file();
	if chan == "":
		print "Chan";
		print "> ",;chan = sys.stdin.readline().split("\n")[0];
	if pseudo == "":
		print "Pseudo";
		print "> ",;pseudo = sys.stdin.readline().split("\n")[0];
	if password == "":
		print "Password";
		print "> ",;password = sys.stdin.readline().split("\n")[0];



def get_converttable():
	if os.path.isfile("kana.list") == False:
		print "kana.list introuvable !";
		sys.exit();
	fichier = open("kana.list", "r");
	contenu = fichier.read();
	lines = contenu.split("\n");
	for line in lines:
		tmp = line.split("\t");
		if len(tmp) >= 2:
			converttable.append(tmp);
			

def kana2romaji(kana):
	for line in converttable:
		kana = kana.replace(line[1], line[0]);
	kana = re.sub("(.)ー", r"\1\1", kana);
	kana = re.sub("っ(.)", r"\1\1", kana);
	kana = re.sub("ッ(.)", r"\1\1", kana);
	return kana.replace("ouu","ōu").replace("uu","ū").replace("oo","ō").replace("ou","ō");


# Main
def main():
	reload(sys);
	sys.setdefaultencoding('utf8');
	get_converttable();
	get_args();
	for item in converttable:
		print item[1] + " -> " + item[0];
	while True:
		mybot().start();
		time.sleep(30);

main();
