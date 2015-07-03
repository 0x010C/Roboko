# -*- coding: utf-8 -*-

import httplib;
import calendar;
import time;
import re;
import urllib;

import Roboko_feed as rbk_feed;

old_timestamp = calendar.timegm(time.gmtime());

def check_new_section(irc, page_link):
	global old_timestamp;
	timestamp = calendar.timegm(time.gmtime());
	entries = rbk_feed.get_new_entries_atom(page_link, old_timestamp);
	for item in entries:
		conn = httplib.HTTPSConnection("fr.wikipedia.org");
		conn.request("GET", item.id[24:]);
		print item.id[24:];
		result = re.findall('<td class="diff-addedline"><div>==(.+)==.*</div></td>', conn.getresponse().read());
		if len(result) > 0:
			if result[0][0] != '=':
				result[0] = result[0].strip();
				tmp = u"\00313\002Nouveau sujet sur le Manga café\002\003 par \00303"+item.author+u"\003 : \00310https://fr.wikipedia.org/wiki/Discussion_Projet:Animation_et_bande_dessinée_asiatiques#"+urllib.quote_plus(result[0].replace(" ", "_"))+u"\003";
				print tmp.encode('utf-8');
				irc.send(irc.chan, tmp.encode('utf-8'));
				time.sleep(2);
	old_timestamp = timestamp;
