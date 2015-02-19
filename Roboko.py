#!/usr/bin/python
# -*- coding: utf-8 -*-
#Autor: Antoine Lamielle "0x010C"
#Date: 19 february 2015
#License: GNU GPL v3

import httplib;
import time;
import os;
import sys;
from feedparser import parse;
import irclib;
import ircbot;
import re;
import unicodedata;

#Paramètres
chan = "##test42";
pseudo = "kiwi_0x010D";
password = "";
server = "holmes.freenode.net";
port = 6667;

wait = 60;
cat = "https://fr.wikipedia.org/w/api.php?hidebots=1&days=7&limit=50&target=Catégorie:Portail:Animation+et+bande+dessinée+asiatiques/Articles+liés&hidewikidata=1&action=feedrecentchanges&feedformat=atom&from=";
page = "";

old_timestamp1 = time.strftime("%Y%m%d%H%M%S", time.gmtime());
old_timestamp2 = time.strftime("%Y%m%d%H%M%S", time.gmtime());


# Boucle principale + Gestion de la lecture et de l'écriture IRC
class mybot(ircbot.SingleServerIRCBot):
	def __init__(self):
		ircbot.SingleServerIRCBot.__init__(self, [(server, port)],pseudo, "Projet abda sur wikipedia francophone");
	
	def on_welcome(self, serv, ev):
		self.saveServ = serv;
		serv.join(chan);
		self.checker();
	
	def on_pubmsg(self, serv, ev):
		author = irclib.nm_to_n(ev.source());
		canal = ev.target();
		message = ev.arguments()[0];
		print author + " --> " + message;
		if re.search("^!jisho .+", message):
			self.jisho(message[7:]);
	
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
	
	def checker(self):
		self.check_new_article(cat);
		#check_new_section(self, bistro);
		self.saveServ.execute_delayed(wait/4, self.checker);
	
	def jisho(self, message):
		self.send(chan, "Traduction de #" + message + "#");

	# Les checkers
	def check_new_article(self, cat_link):
		global old_timestamp1;
		timestamp1 = time.strftime("%Y%m%d%H%M%S", time.gmtime());
		entries = get_entries(cat_link + old_timestamp1);
		for item in entries:
			if re.search("\n<p><b>Nouvelle page</b></p>", item.summary):
				tmp = u"- Nouvel article : [["+ item.title + u"]] - " + article_link(item.title);
				print tmp;
				self.act(chan, tmp);
				time.sleep(2);
			else:
				tmp = u"- Modification de l'article [["+ item.title + u"]] - " + article_link(item.title);
				print tmp;
				self.act(chan, tmp);
				time.sleep(2);
		old_timestamp1 = timestamp1;


# Gestion du temps
def timestampisation(date):
	return time.mktime(time.strptime(date,"%Y-%m-%dT%H:%M:%SZ")) + (2*60*60);

# Recuperation de feed rss
def get_entries(link):
	feed = parse(link);
	return feed['entries'];

# Divers
def article_link(link):
	return "https://fr.wikipedia.org/wiki/" + link;

# Main
def main():
	mybot().start();

main();
