# -*- coding: utf8 -*-
#!/usr/bin/python
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

#Paramètres
chan = "##test42";
pseudo = "kiwi_0x010D";
password = "";
server = "holmes.freenode.net";
port = 6667;
wait = 60;

# Boucle principale + Gestion de la lecture et de l'écriture IRC
class mybot(ircbot.SingleServerIRCBot):
	def __init__(self):
		ircbot.SingleServerIRCBot.__init__(self, [(server, port)],pseudo, "Test de Bot");
	
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
		self.saveServ.privmsg(to, message);
	
	def checker(self):
		print "check";
		self.saveServ.execute_delayed(wait/4, self.checker);
	
	def jisho(self, message):
		print "Traduction de #" + message + "#";


# Recuperation de feed rss
def get_entries(link):
	feed = parse(link);
	return feed;

def get_last_entrie(link):
	feed = get_entries(link);
	return feed['entries'][0];


# Main
def main():
	mybot().start();

main();
