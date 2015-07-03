# -*- coding: utf-8 -*-

import time;
import re;
from feedparser import parse;
import urllib;
import calendar;
import datetime;
import httplib;

import Roboko_utils as rbk_utils;



# Gestion du temps
def timestampisation(date):
	return time.mktime(time.strptime(date,"%Y-%m-%dT%H:%M:%SZ"));
	
def timestampisation2(date):
	tz = int(re.findall("^.+([-+][0-9]{2})[0-9]{2}$", date)[0]);
	d = re.findall("^[a-zA-Z]+, (.+) [-+][0-9]{4}$", date)[0];
	return time.mktime(time.strptime(d,"%d %b %Y %H:%M:%S")) - (tz*3600);

# Recuperation de feed rss/atom brut
def get_entries(link):
	feed = parse(link);
	return feed['entries'];

# Recuperation de feed rss
def get_new_entries_rss(link, old_timestamp):
	try:
		feed = get_entries(link);
	except:
		print "Unable to get "+link;
		feed = []
	entries = [];
	for item in feed:
		try:
			if int(timestampisation2(item.published)) > int(old_timestamp): # Attention, le serveur doit être en UTC
				entries.append(item);
		except:
			print "bad date";
	return entries;

# Recuperation de feed atom
def get_new_entries_atom(link, old_timestamp):
	feed = get_entries(link);
	entries = [];
	for item in feed:
		if int(timestampisation(item.updated)) > int(old_timestamp): # Attention, le serveur doit être en UTC
			entries.append(item);
	return entries;

