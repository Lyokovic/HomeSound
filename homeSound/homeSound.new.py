#! /usr/bin/python2
# -*- coding:utf-8 -*-

from player import Player
import redis

radioPlaying = '0'
airPlaying = '0'

class HomeSound:
    def __init__(self):
	self.r = redis.StrictRedis()
	self.player = Player()
	self.player.setUri(self.r.get('/radio/'+self.r.get('/radio/current')+'/uri'))
	self.player.play()

# Active la fonction radio (ne lis que si airplay ne joue pas)
    def enableRadio(self):
	self.r.set('/radioPlaying','1')
	if airPlaying == '0':
	    radioPlaying = '1'
	    self.player.play()

# D√sactive la fonction radio
    def disableRadio(self):
	self.r.set('/radioPlaying','0')
	radioPlaying = '0'
	self.player.stop()

# D√©marre la fonction radio (ne lis que si la lecture est activ√e dans redis)
    def startRadio(self):
	play = self.r.get('/radioPlaying')
	if play == '1':
	    radioPlaying = '1'
	    self.player.play()
    
# Stoppe la fonction radio
    def stopRadio(self):
	radioPlaying = '0'
	self.player.stop()

    def changeCurrentRadio(self,id):
	choice = self.r.get('/radio/'+msg+'/uri')
	if choice != None:
	    self.player.stop()
	    self.r.set('/radio/current',msg)
	    self.player.setUri(choice)

    def toogleAirPlay(self,state):
	if state == '1':
	   airPlaying = '1'
	   self.stopRadio()
	else :
	    airPlaying = '0'
	    self.startRadio()

    def toogleRadioPlay(self,id):
	print "ToogleRadioPlay"
	if id == '':
	    self.enableRadio()
	elif id == '-1':
	    self.disableRadio()
	else:
	    self.changeCurrentRadio(id)
	    self.enableRadio()

    def run(self):
	ps = self.r.pubsub()
	ps.subscribe('/radioPlay')
	ps.subscribe('/airPlaying')

	for item in ps.listen():
	    chan = item['channel']
	    msg = item['data']
	    
	    if item['type'] == 'message':
		if chan == '/radioPlay':
		    self.toogleRadioPlay(msg)

		elif chan == '/airPlaying':
		    self.toogleAirPlay(msg)

def main():
    homeSound = HomeSound()
    homeSound.run()

if __name__ == '__main__':
    main()
