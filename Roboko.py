#!/usr/bin/python
# -*- coding: utf-8 -*-
#Autor: Antoine Lamielle "0x010C"
#Date: 19 february 2015
#License: GNU GPL v3

import sys
import time
import urllib
import json

# Roboko
import Roboko_args as rbk_args
import Roboko_jisho as rbk_jisho
import Roboko_seen as rbk_seen
import Roboko_irc as rbk_irc

#Paramètres
version = "2.03"

chan = ""
pseudo = ""
password = ""
server = ""
port = 0
wait = 0


			




# Main
def main():
	global chan, pseudo, password, server, port, wait, version
	reload(sys)
	sys.setdefaultencoding('utf8')
	rbk_jisho.get_converttable()
	rbk_seen.init()
	(chan,pseudo,password,server,port,wait) = rbk_args.get_args()

	while True:
		rbk_irc.mybot(server, port, chan, pseudo, password, wait, version).start()
		time.sleep(30)


main()
