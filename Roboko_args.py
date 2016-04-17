# -*- coding: utf-8 -*-

import os;
import re;
import sys;

def parse_config_file():
	chan = "";
	pseudo = "";
	password = "";
	server = "chat.freenode.net";
	port = 6697;
	wait = 300;

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

	return (chan,pseudo,password,server,port,wait);

def get_args():
	(chan,pseudo,password,server,port,wait) = parse_config_file();
	if chan == "":
		print "Chan";
		print "> ",;chan = sys.stdin.readline().split("\n")[0];
	if pseudo == "":
		print "Pseudo";
		print "> ",;pseudo = sys.stdin.readline().split("\n")[0];
	if password == "":
		print "Password";
		print "> ",;password = sys.stdin.readline().split("\n")[0];

	return (chan,pseudo,password,server,port,wait);
