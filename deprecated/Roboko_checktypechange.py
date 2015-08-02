# -*- coding: utf-8 -*-

import httplib;
import calendar;
import time;
import re;

import Roboko_feed as rbk_feed;


r1 = re.compile(ur"\{\{Infobox Animation et bande dessinée asiatiques/Entête(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*type *=([^\}\|]*)");
r2 = re.compile(ur"\{\{Infobox Animation et bande dessinée asiatiques/Livre(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{(?:[^\}\{]|\{\{[^\}]*\}\})*\}\})*\}\})*public_cible *=([^\}\|]*)");

old_timestamp = calendar.timegm(time.gmtime());


def check_type_change(irc, cat):
	global old_timestamp, r1, r2;
	timestamp = calendar.timegm(time.gmtime());
	entries = rbk_feed.get_new_entries_atom(cat, old_timestamp);
	for item in entries:
		conn = httplib.HTTPSConnection("fr.wikipedia.org");
		conn.request("GET", u"/w/api.php?format=json&action=query&list=users&usprop=groups&ususers="+item.author.replace(" ", "_"));
		autopatrolled = False;
		try:
			if "autopatrolled" in json.loads(conn.getresponse().read())["query"]["users"][0]["groups"]:
				autopatrolled = True;
		except:
			print "";
		if not autopatrolled:
			try:
				conn = httplib.HTTPSConnection("fr.wikipedia.org");
				conn.request("GET", u"/w/api.php?action=query&prop=revisions&rvprop=content&rvlimit=2&continue&format=json&titles="+item.title.replace(" ", "_"));
				revs = json.loads(conn.getresponse().read())["query"]["pages"].itervalues().next()["revisions"]
				rbk_utils.T("Check type change", revs);

				try:
					type1 = r1.findall(revs[0]["*"])[0].replace("\n", "").strip().lower();
					type2 = r1.findall(revs[1]["*"])[0].replace("\n", "").strip().lower();
					if type1 != type2:
						tmp = item.author+u" a modifié le type de [["+item.title+u"]], de \""+type2+u"\" à \""+type1+u"\" — https://fr.wikipedia.org/wiki/Special:Diff/"+re.sub(".*diff=([0-9]+).*", r"\1", entries[0].id);
						irc.send(irc.chan, tmp.encode('utf-8'));
				except:
					print "";

				try:
					type1 = r2.findall(revs[0]["*"])[0].replace("\n", "").strip().lower();
					type2 = r2.findall(revs[1]["*"])[0].replace("\n", "").strip().lower();
					if type1 != type2:
						tmp = item.author+u" a modifié le type de [["+item.title+u"]], de \""+type2+u"\" à \""+type1+u"\" — https://fr.wikipedia.org/wiki/Special:Diff/"+re.sub(".*diff=([0-9]+).*", r"\1", entries[0].id);
						irc.send(irc.chan, tmp.encode('utf-8'));
				except:
					print "";
			except:
				print "";
	old_timestamp = timestamp;
