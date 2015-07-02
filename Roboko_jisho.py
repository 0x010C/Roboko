# -*- coding: utf-8 -*-

import httplib;
import os;
import urllib;
import re;


converttable = [];

def get_converttable():
	global converttable;
	if os.path.isfile("kana.list") == False:
		print "kana.list introuvable !";
		sys.exit();
	fichier = open("kana.list", "r");
	contenu = fichier.read();
	lines = contenu.split("\n");
	for line in lines:
		tmp = line.split("\t");
		if len(tmp) >= 2:
			converttable.append(tmp);

def translate(message):
		conn = httplib.HTTPConnection("tangorin.com");
		conn.request("GET", "/general/"+urllib.quote_plus(message));
		result = re.findall('<div class="entry"><a class="btn btn-link entry-menu" onclick="entryMenu\(this,\{\n([\s\S]+)</div>', conn.getresponse().read());
		if len(result) > 0:
			result = result[0].split("\">")[0].split("\n")[2:6];
			for line in result:
				line = line.split(":")[1];
			kanji = re.findall("'(.*)'",result[0])[0];
			kana = re.findall("'(.*)'",result[1])[0].split("・")[0];
			trad = re.findall("'(.*)'",result[3])[0].replace("<ol>", "").replace("</ol>", "").replace("</li><li>", " - ").replace("<li>", "").replace("</li>", "").replace("\\", "");
			output = "\00313" + kanji + "\003[\00305" + kana + "\003, \00307" + kana2romaji(kana) + "\003] --> \003" + trad + "\003";
			return output.encode('utf-8');
		else:
			trad = kana2romaji(message);
			if trad != message:
				return "\00304Introuvable, tentative de transcription\003 : " + trad;
			else:
				return "\00304Introuvable\003";

def kana2romaji(kana):
	for line in converttable:
		kana = kana.replace(line[1], line[0]);
	kana = re.sub("(.)ー", r"\1\1", kana);
	kana = re.sub("っ(.)", r"\1\1", kana);
	kana = re.sub("ッ(.)", r"\1\1", kana);
	return kana.replace("ouu","ōu").replace("uu","ū").replace("oo","ō").replace("ou","ō");
