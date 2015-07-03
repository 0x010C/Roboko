# -*- coding: utf-8 -*-

import calendar;
import time;
import urllib;

import Roboko_feed as rbk_feed;

old_timestamp = calendar.timegm(time.gmtime());

def check_new_news(irc):
	global old_timestamp;
	timestamp = calendar.timegm(time.gmtime());

	entries = rbk_feed.get_new_entries_rss(u"http://www.animenewsnetwork.com/news/rss.xml", old_timestamp);
	for item in entries:
		tmp = u"[ANN] "+item.title+u" – http://4nn.cx/"+item.link.split("/")[-1];
		irc.send(irc.chan, tmp.encode('utf-8'));

	entries = rbk_feed.get_new_entries_rss(u"http://www.animeland.com/rss/news", old_timestamp);
	for item in entries:
		tmp = u"[Animeland] "+item.title+u" – "+u"/".join(item.link.replace(u" ", u"_").split(u"/")[:-1])+u"/";
		irc.send(irc.chan, tmp.encode('utf-8'));

	old_timestamp = timestamp;
