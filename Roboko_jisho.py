# -*- coding: utf-8 -*-

import httplib
import os
import urllib
import re


converttable = []
prev_translation = ""

def get_converttable():
	global converttable
	if os.path.isfile("kana.list") == False:
		print "kana.list introuvable !"
		sys.exit()
	fichier = open("kana.list", "r")
	contenu = fichier.read()
	lines = contenu.split("\n")
	for line in lines:
		tmp = line.decode("utf8").split("\t")
		if len(tmp) >= 2:
			converttable.append(tmp)

def translate(message):
	global prev_translation

	message = message.strip(' \t\n\r')

	if message == prev_translation:
		return translate_word_by_word(message)

	prev_translation = message
	return translate_all(message)

def translate_all(message, split=False):
	conn = httplib.HTTPConnection("tangorin.com")
	conn.request("GET", "/general/"+urllib.quote_plus(message))
	result = re.findall('<div class="entry"><a class="btn btn-link entry-menu" onclick="entryMenu\(this,\{\n([\s\S]+)</div>', conn.getresponse().read())
	if len(result) > 0:
		result = result[0].split("\">")[0].split("\n")[2:6]
		for line in result:
			line = line.split(":")[1]
		kanji = re.findall("'(.*)'",result[0])[0]
		kana = re.findall("'(.*)'",result[1])[0].split("・")[0]
		trad = re.findall("'(.*)'",result[3])[0].replace("<ol>", "").replace("</ol>", "").replace("</li><li>", " - ").replace("<li>", "").replace("</li>", "").replace("\\", "")
		output = "\00313" + kanji + "\003[\00305" + kana + "\003, \00307" + kana2romaji(kana) + "\003] --> \003" + trad + "\003"
		return output.encode('utf-8')

	trad = kana2romaji(message)
	if trad != message and not split:
		return "\00304Introuvable, tentative de transcription\003 : " + trad

	return "\00304Introuvable\003"

def translate_word_by_word(message):
	words = message.split(" ")
	print len(words)
	if len(words) < 2:
		return translate_all(message)

	trad = kana2romaji(message)
	result = ""
	if trad != message:
		result = "\00303\002Transcription globale :\002\003 " + trad + "\n"
	result += "\00303\002Traduction mot par mot :\002\003"
	for word in words:
		result += "\n" + word + " : " + translate_all(word, True)

	return result


def kana2romaji(kana):
	for line in converttable:
		kana = kana.replace(line[1], line[0])
	kana = re.sub("(.)ー", r"\1\1", kana)
	kana = re.sub("っ(.)", r"\1\1", kana)
	kana = re.sub("ッ(.)", r"\1\1", kana)
	return kana.replace("ouu","ōu").replace("uu","ū").replace("oo","ō").replace("ou","ō")
