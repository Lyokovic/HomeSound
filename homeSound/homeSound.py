#! /usr/bin/python2
# -*- coding:utf-8 -*-

from player import Player
import redis
import signal,sys

class HomeSound:
    def __init__(self):
	self.r = redis.StrictRedis()
	self.player = Player()
	self.player.setUri(self.r.get('/radio/'+self.r.get('/radio/current')+'/uri'))


    # Get (no arg) or Set (arg='0'/'1') redis /radioPlaying value
    def radioPlaying(self,val=''):
        if val == '':
            return self.r.get('/radioPlaying')
        else:
            self.r.set('/radioPlaying',val)

    # Get (no arg) or Set (arg='0'/'1') redis /airPlaying value
    def airPlaying(self,val=''):
        if val == '':
            return self.r.get('/airPlaying')
        else:
            self.r.set('/airPlaying',val)

    def changeCurrentRadio(self,id):
	choice = self.r.get('/radio/'+id+'/uri')
	if choice != None:
	    self.player.stop()
	    self.r.set('/radio/current',id)
	    self.player.setUri(choice)
            print 'Setting radio '+id
        else:
            print "Erreur, id ("+id+") de radio inconnu."

    def toogleAirPlay(self,state):
        if state == '1':
            self.airPlaying('1')
            self.player.stop()
            print 'AirPlay starts'
        else :
            self.airPlaying('0')
            print 'AirPlay stops'
            if self.radioPlaying() == '1':
                self.player.play()
                print 'Resume radio playing'

    def toogleRadioPlay(self,id):
	if id == '-1':
            print 'Stop playing radio'
            self.radioPlaying('0')
            self.player.stop()
	else:
            if id != '':
                self.changeCurrentRadio(id)
            self.radioPlaying('1')
            if self.airPlaying() == '0':
                self.player.play()
                print 'Playing radio'

    def sendUpdate(self):
        update = '0'
        #if self.radioPlaying() == '1':
        #    if self.airPlaying() == '1':
        #        update = '2'
        #    else:
        #        update = '1'

        self.r.publish('/playing',update)

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
            self.sendUpdate()


homeSound = HomeSound()

def sigint_handler(signal,frame):
    print
    homeSound.toogleRadioPlay('-1')
    print "Bye ;)"
    sys.exit(1)

def main():
    signal.signal(signal.SIGINT, sigint_handler)
    homeSound.run()

if __name__ == '__main__':
    main()
