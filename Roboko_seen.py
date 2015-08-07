# -*- coding: utf-8 -*-

import time
import calendar
import pickle

import Roboko_utils as rbk_utils

TIMEZONE = 2
seentable = {}

def init():
	global seentable
	try:
		seentable = pickle.load(open("log/seen.log", "r"))
	except:
		seentable = {}
		pickle.dump(seentable, open("log/seen.log", "w"))

def save(user, message):
	global seentable
	seentable[user] = {"timestamp":calendar.timegm(time.gmtime()), "message":message}
	pickle.dump(seentable, open("log/seen.log", "w"))

def get(irc, user):
	global seentable
	user = user.split(" ")[0]
	print "#"+user+"#"
	if user in irc.channels[irc.chan].users():
		return u"Regarde mieux, " + user + " est sur le chan )"
	if user in seentable:
		return user + u" a été aperçu pour la dernière fois il y a " + rbk_utils.timestampToInterval(seentable[user]["timestamp"]) + ", le " + rbk_utils.timestampToDate(seentable[user]["timestamp"]+(3600*TIMEZONE)) + " (" + seentable[user]["message"] + ")"
	else:
		return u"Je n'ai jamais vu cet utiliateur..."
