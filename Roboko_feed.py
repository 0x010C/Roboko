# -*- coding: utf-8 -*-

import time;
import re;
from feedparser import parse;
import urllib;
import calendar;
import datetime;
import httplib;


old_timestamp1 = calendar.timegm(time.gmtime());
old_timestamp2 = calendar.timegm(time.gmtime());
old_timestamp3 = calendar.timegm(time.gmtime());
old_timestamp4 = calendar.timegm(time.gmtime());


r1 = re.compile(ur"\{\{Infobox Animation et bande dessinée asiatiques/Entête(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*type *=([^\}\|]*)");
r2 = re.compile(ur"\{\{Infobox Animation et bande dessinée asiatiques/Livre(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*public_cible *=([^\}\|]*)");


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


# Divers
def article_link(link):
	return "https://fr.wikipedia.org/wiki/" + urllib.quote_plus(link.replace(" ", "_")).replace(".$", "%2E");









# Les checkers
def check_new_article(irc, cat):
	global old_timestamp1;
	timestamp1 = calendar.timegm(time.gmtime());
	entries = get_new_entries_atom(cat, old_timestamp1);
	for item in entries:
		if re.search("\n<p><b>Nouvelle page</b></p>", item.summary):
			tmp = u"\00313\002Nouvel article\002\003 : [[\00307"+ item.title + u"\003]] – \00310" + article_link(item.title.encode('utf-8')) + "\003";
			irc.send(chan, tmp.encode('utf-8'));
			time.sleep(2);
#			else:
#				if isIp(item.author):
#					tmp = u"- Modification de [["+ item.title + u"]] par " + item.author + u" - " + article_link(item.title.encode('utf-8'));
#					print tmp;
#					irc.act(chan, tmp.encode('utf-8'));
#					time.sleep(2);
	old_timestamp1 = timestamp1;
	
def check_new_section(irc, page_link):
	global old_timestamp2;
	timestamp2 = calendar.timegm(time.gmtime());
	entries = get_new_entries_atom(page_link, old_timestamp2);
	conn = httplib.HTTPSConnection("fr.wikipedia.org");
	for item in entries:
		conn.request("GET", item.id[24:]);
		print item.id[24:];
		result = re.findall('<td class="diff-addedline"><div>==(.+)==.*</div></td>', conn.getresponse().read());
		if len(result) > 0:
			if result[0][0] != '=':
				result[0] = result[0].strip();
				tmp = u"\00313\002Nouveau sujet sur le Manga café\002\003 par \00303"+item.author+u"\003 : \00310https://fr.wikipedia.org/wiki/Discussion_Projet:Animation_et_bande_dessinée_asiatiques#"+urllib.quote_plus(result[0].replace(" ", "_"))+u"\003";
				print tmp.encode('utf-8');
				irc.send(chan, tmp.encode('utf-8'));
				time.sleep(2);
	old_timestamp2 = timestamp2;
	
def check_new_news(irc):
	global old_timestamp3;
	timestamp3 = calendar.timegm(time.gmtime());

	entries = get_new_entries_rss(u"http://www.animenewsnetwork.com/news/rss.xml", old_timestamp3);
	for item in entries:
		tmp = u"[ANN] "+item.title+u" – http://4nn.cx/"+item.link.split("/")[-1];
		irc.send(chan, tmp.encode('utf-8'));

	entries = get_new_entries_rss(u"http://www.animeland.com/rss/news", old_timestamp3);
	for item in entries:
		tmp = u"[Animeland] "+item.title+u" – "+u"/".join(item.link.replace(u" ", u"_").split(u"/")[:-1])+u"/";
		irc.send(chan, tmp.encode('utf-8'));

	old_timestamp3 = timestamp3;

def check_type_change(irc, cat):
	global old_timestamp4, r1, r2;
	timestamp4 = calendar.timegm(time.gmtime());
	entries = get_new_entries_atom(cat, old_timestamp4);
	conn = httplib.HTTPSConnection("fr.wikipedia.org");
	for item in entries:
		conn.request("GET", u"/w/api.php?format=json&action=query&list=users&usprop=groups&ususers="+item.author.replace(" ", "_"));
		autopatrolled = False;
		try:
			if "autopatrolled" in json.loads(conn.getresponse().read())["query"]["users"][0]["groups"]:
				autopatrolled = True;
		except:
			print "";
		if not autopatrolled:
			try:
				conn.request("GET", u"/w/api.php?action=query&prop=revisions&rvprop=content&rvlimit=2&continue&format=json&titles="+item.title.replace(" ", "_"));
				revs = json.loads(conn.getresponse().read())["query"]["pages"].itervalues().next()["revisions"]
				T("Check type change", revs);

				try:
					type1 = r1.findall(revs[0]["*"])[0].replace("\n", "").strip().lower();
					type2 = r1.findall(revs[1]["*"])[0].replace("\n", "").strip().lower();
					if type1 != type2:
						tmp = item.author+u" a modifié le type de [["+item.title+u"]], de \""+type2+u"\" à \""+type1+u"\" — https://fr.wikipedia.org/wiki/Special:Diff/"+re.sub(".*diff=([0-9]+).*", r"\1", entries[0].id);
						irc.send(chan, tmp.encode('utf-8'));
				except:
					print "";

				try:
					type1 = r2.findall(revs[0]["*"])[0].replace("\n", "").strip().lower();
					type2 = r2.findall(revs[1]["*"])[0].replace("\n", "").strip().lower();
					if type1 != type2:
						tmp = item.author+u" a modifié le type de [["+item.title+u"]], de \""+type2+u"\" à \""+type1+u"\" — https://fr.wikipedia.org/wiki/Special:Diff/"+re.sub(".*diff=([0-9]+).*", r"\1", entries[0].id);
						irc.send(chan, tmp.encode('utf-8'));
				except:
					print "";
			except:
				print "";
	old_timestamp4 = timestamp4;
