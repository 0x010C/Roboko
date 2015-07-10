# -*- coding: utf-8 -*-

import time;
import calendar;
import pickle;

import Roboko_utils as rbk_utils;

TIMEZONE = 2;
seentable = {};

def init():
	global seentable;
	try:
		seentable = pickle.load(open("log/seen.log", "r"));
		print seentable;
	except:
		seentable = {};
		pickle.dump(seentable, open("log/seen.log", "w"));

def save(user, message):
	global seentable;
	seentable[user] = {"timestamp":calendar.timegm(time.gmtime()), "message":message};
	pickle.dump(seentable, open("log/seen.log", "w"));

def get(irc, user):
	global seentable;
	user = user.split(" ")[0];
	print "#"+user+"#";
	if user in seentable:
		if user in irc.channels[irc.chan].users():
			return u"Regardes mieux, " + user + " est sur le chan ;)"
		else:
			return user + u" a été aperçu pour la dernière fois il y a " + rbk_utils.timestampToInterval(seentable[user]["timestamp"]) + ", le " + rbk_utils.timestampToDate(seentable[user]["timestamp"]) + " (" + seentable[user]["message"] + ")";
	else:
		return u"Je n'ai jamais vu cet utiliateur...";