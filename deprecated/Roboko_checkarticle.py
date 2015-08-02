# -*- coding: utf-8 -*-

import calendar;
import time;
import re;

import Roboko_feed as rbk_feed;
import Roboko_utils as rbk_utils;

old_timestamp = calendar.timegm(time.gmtime());

def check_new_article(irc, cat):
	global old_timestamp;
	timestamp = calendar.timegm(time.gmtime());
	entries = rbk_feed.get_new_entries_atom(cat, old_timestamp);
	for item in entries:
		if re.search("\n<p><b>Nouvelle page</b></p>", item.summary):
			tmp = u"\00313\002Nouvel article\002\003 : [[\00307"+ item.title + u"\003]] – \00310" + rbk_utils.article_link(item.title.encode('utf-8')) + "\003";
			irc.send(irc.chan, tmp.encode('utf-8'));
			time.sleep(2);
	old_timestamp = timestamp;
