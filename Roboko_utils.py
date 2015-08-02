# -*- coding: utf-8 -*-

import time;
import re;
import urllib;
import datetime;
import calendar;


def T(title, message):
	try:
		tracefile = open("trace/"+time.strftime('%Y-%m-%d',time.localtime())+".log", "a");
		tracefile.write(time.strftime('%H:%M:%S',time.localtime())+"> "+title.encode("utf-8")+"\n=============================================================\n"+message.encode("utf-8")+"\n\n\n\n");
		tracefile.close();
	except:
		print "Couldn't trace";




def isIp(name):
	if re.search("^[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}.[0-9]{1,3}$", name):
		return True;
	else:
		if re.search("^[0-9a-fA-F]{0,4}:[0-9a-fA-F]{0,4}:[0-9a-fA-F]{0,4}:[0-9a-fA-F]{0,4}:[0-9a-fA-F]{0,4}:[0-9a-fA-F]{0,4}:[0-9a-fA-F]{0,4}:[0-9a-fA-F]{0,4}$", name):
			return True;
		else:
			return False;
			

def article_link(link):
	return "https://fr.wikipedia.org/wiki/" + urllib.quote_plus(link.replace(" ", "_")).replace(".$", "%2E");


def monthToString(month):
	if month == 1:
		return "janvier";
	elif month == 2:
		return "février";
	elif month == 3:
		return "mars";
	elif month == 4:
		return "avril";
	elif month == 5:
		return "mai";
	elif month == 6:
		return "juin";
	elif month == 7:
		return "juillet";
	elif month == 8:
		return "août";
	elif month == 9:
		return "septembre";
	elif month == 10:
		return "octobre";
	elif month == 11:
		return "novembre";
	elif month == 12:
		return "décembre";

def timestampToDate(timestamp):
	t = datetime.datetime.fromtimestamp(timestamp);
	return t.strftime("%d ") + monthToString(int(t.strftime("%m"))) + " à " + t.strftime("%H:%M")

def timestampToInterval(timestamp):
	dt = calendar.timegm(time.gmtime()) - timestamp;
	if dt < 60:
		return "il y a moins d'une minute";
	elif dt < 120:
		return "il y a une minute";
	elif dt < 3600:
		return str(dt/60) + " minutes";
	elif dt < 7200:
		return "une heure";
	elif dt < 86400:
		return str(dt/3600) + " heures";
	elif dt < 172800:
		return "un jour";
	else:
		return str(dt/86400) + " jours";
