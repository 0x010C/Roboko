# -*- coding: utf-8 -*-

import time;
import re;
import urllib;


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
		if re.search("^[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}:[0-9a-f]{0,4}$", name):
			return True;
		else:
			return False;
			

def article_link(link):
	return "https://fr.wikipedia.org/wiki/" + urllib.quote_plus(link.replace(" ", "_")).replace(".$", "%2E");
