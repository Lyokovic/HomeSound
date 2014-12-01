#! /usr/bin/python2
# -*- coding:utf-8 -*-

from player import Player
from speakers import Speakers
import redis
import signal,sys

class HomeSound:
    def __init__(self):
	self.r = redis.StrictRedis()
	self.player = Player()
	self.speakers = Speakers()
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

    def toogleDevice(self,chan,id):
	pin = self.r.get('/device/'+id+'/audioPin')
        state = self.r.get('/device/'+id+'/enabled')
	if pin != None and state != None:
            if chan == '/device/toogle':
                if state == '0':
                    self.speakers.enable(pin)
                    self.r.set('/device/'+id+'/enabled','1')
                else:
                    self.speakers.disable(pin)
                    self.r.set('/device/'+id+'/enabled','0')

            elif chan == '/device/enable':
                self.speakers.enable(pin)
                self.r.set('/device/'+id+'/enabled','1')
            else:
                self.speakers.disable(pin)
                self.r.set('/device/'+id+'/enabled','0')
        else:
            print "Erreur, id ("+id+") d'enceinte inconnu."

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

	ps.subscribe('/device/enable')
	ps.subscribe('/device/disable')
	ps.subscribe('/device/toogle')

	for item in ps.listen():
	    chan = item['channel']
	    msg = item['data']
	    
	    if item['type'] == 'message':
		if chan == '/radioPlay':
		    self.toogleRadioPlay(msg)

		elif chan == '/airPlaying':
		    self.toogleAirPlay(msg)

                elif chan[:7] == '/device':
		    self.toogleDevice(chan,msg)
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
