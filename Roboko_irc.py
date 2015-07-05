# -*- coding: utf-8 -*-


import irclib;
import ircbot;
import time;
import re;

import Roboko_utils as rbk_utils;
import Roboko_feed as rbk_feed;
import Roboko_jisho as rbk_jisho;
import Roboko_checkarticle as rbk_ca;
import Roboko_checknews as rbk_cn;
import Roboko_checksection as rbk_cs;
import Roboko_checktypechange as rbk_ctc;



logfile = None;

cat = "https://fr.wikipedia.org/w/api.php?hidebots=1&days=7&limit=50&target=Catégorie:Portail:Animation+et+bande+dessinée+asiatiques/Articles+liés&hidewikidata=1&action=feedrecentchanges&feedformat=atom";
page = "https://fr.wikipedia.org/w/index.php?title=Discussion_Projet:Animation_et_bande_dessin%C3%A9e_asiatiques&feed=atom&action=history";


# Boucle principale + Gestion de la lecture et de l'écriture IRC
class mybot(ircbot.SingleServerIRCBot):
	def __init__(self, server, port, chan, pseudo, password, wait, version):
		self.chan = chan;
		self.password = password;
		self.wait = wait;
		self.version = version;
		ircbot.SingleServerIRCBot.__init__(self, [(server, port)],pseudo, "Roboko v"+version);

	def on_welcome(self, serv, ev):
		self.saveServ = serv;
		if self.password != "":
			self.send("nickserv", "identify " + self.password);
			time.sleep(10);
		serv.join(self.chan);
		self.checker();

	def on_privnotice(self, serv, ev):
		print "#" + irclib.nm_to_n(ev.source()) + "# --> " + ev.arguments()[0];

	def on_pubmsg(self, serv, ev):
		author = irclib.nm_to_n(ev.source());
		canal = ev.target();
		message = ev.arguments()[0];
		if canal == self.chan:
			self.log("<"+author+"> "+message);
		self.command(author, canal, message);

	def on_action(self, serv, ev):
		author = irclib.nm_to_n(ev.source());
		canal = ev.target();
		message = ev.arguments()[0];
		if canal == self.chan:
			self.log("<"+author+"> "+author+" "+message);
		self.command(author, canal, message);

	def on_nick(self, serv, ev):
		self.log("<*> "+irclib.nm_to_n(ev.source())+u" s'appelle à présent "+ev.target());

	def on_join(self, serv, ev):
		self.log("<*> "+irclib.nm_to_n(ev.source())+u" a rejoint le canal");

	def on_part(self, serv, ev):
		if len(ev.arguments()) > 0:
			self.log("<*> "+irclib.nm_to_n(ev.source())+u" a quitté le canal ("+ev.arguments()[0]+u")");
		else:
			self.log("<*> "+irclib.nm_to_n(ev.source())+u" a quitté le canal");

	def on_quit(self, serv, ev):
		if len(ev.arguments()) > 0:
			self.log("<*> "+irclib.nm_to_n(ev.source())+u" a quitté le serveur ("+ev.arguments()[0]+u")");
		else:
			self.log("<*> "+irclib.nm_to_n(ev.source())+u" a quitté le serveur");

	def on_kick(self, serv, ev):
		self.log("<*> "+irclib.nm_to_n(ev.source())+u" a expulsé "+ev.arguments()[0]+u" ("+ev.arguments()[1]+u")");

	def on_mode(self, serv, ev):
		self.log("<*> "+irclib.nm_to_n(ev.source())+u" a modifié des modes : "+" ".join(ev.arguments()));

	def send(self, to, message):
		try:
			self.saveServ.privmsg(to, message);
			if to == self.chan:
				self.log("<Roboko> "+message);
		except:
			print u"except";

	def send_notice(self, to, message):
		try:
			self.saveServ.notice(to, message);
		except:
			print u"except";

	def act(self, to, message):
		try:
			self.saveServ.action(to, message);
			if to == self.chan:
				self.log("<Roboko> "+message);
		except:
			print u"except";

	def command(self, author, canal, message):
		if re.search("^!help", message):
			self.send(author, "Roboko, bot irc pour le chan du Projet:Animation et bande dessinée asiatiques sur la Wikipédia francophone (##abda)");
			time.sleep(1);
			self.send(author, " ");
			self.send(author, "Commandes disponibles :");
			self.send(author, "!help : affiche ce message d'aide");
			self.send(author, "!jisho : tranduit et transcrit un mot japonais");
			self.send(author, "[[lien interne WP]] : traduit un lien interne en url");
			self.send(author, "Annonce les nouveaux articles du Portail:ABDA");
			self.send(author, "Annonce les nouveaux sujets sur le Manga café");
			time.sleep(1);
			self.send(author, " ");
			self.send(author, "Roboko v"+self.version+", développé par 0x010C en python2.7 d'après les idées de Thibaut120094");
		if re.search("\[\[.+\]\]", message):
			links = re.findall("\[\[([^\[\]\|]+)(?:\|[^\[\]]+)*\]\]", message);
			output = "";
			for link in links:
				if output == "":
					newoutput = rbk_utils.article_link(link.strip());
				else:
					newoutput = output + " - " + rbk_utils.article_link(link.strip());
				if len(newoutput) > 340:
					break;
				output = newoutput;
			self.send(canal, output);
		if re.search("^!jisho .+", message):
			self.send(canal, rbk_jisho.translate(message[7:]));
		if re.search("^!j .+", message):
			self.send(canal, rbk_jisho.translate(message[3:]));
		if (re.search(u"^!exit", message) or re.search(u"^!stop", message)) and self.channels[self.chan].is_oper(author):
			self.send(self.chan, u"\002\00304oyasumi~\003\002")
			sys.exit()
		elif (re.search(u"^!exit", message) or re.search(u"^!stop", message)) and not self.channels[self.chan].is_oper(author):
			self.send_notice(author, u"Vous n'avez pas les droits nécessaires pour me stopper. En cas de dysfonctionnement, vous pouvez contacter Thibaut120094 ou kiwi_0x010C.")
	
	def log(self, message):
		try:
			logfile = open("log/"+time.strftime('%Y-%m-%d',time.localtime())+".log", "a");
			logfile.write(time.strftime('%H:%M:%S',time.localtime())+" "+message.encode("utf-8")+"\n");
			logfile.close();
		except:
			print "Couldn't log a message";

	def checker(self):
		rbk_ca.check_new_article(self, cat);
		rbk_cs.check_new_section(self, page);
		rbk_ctc.check_type_change(self, cat);

		self.saveServ.execute_delayed(self.wait, self.checker);
