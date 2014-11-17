#! /usr/bin/python2
# -*- coding:utf-8 -*-

from player import Player
import redis

r = redis.StrictRedis()

player = Player()
player.setUri(r.get('/radio/'+r.get('/radio/current')+'/uri'))
player.play()

ps = r.pubsub()
ps.subscribe('/radioPlay')
ps.subscribe('/airPlaying')

for item in ps.listen():
    chan = item['channel']
    msg = item['data']
    
    if item['type'] == 'message':
      if chan == '/radioPlay':
	  if msg == '':
	      r.set('/radioPlaying','1')
	      player.play()
	      print 'Playing default radio'
	  elif msg == '-1':
	      r.set('/radioPlaying','0')
	      player.stop()
	      print 'Stop playing radio'
	  else:
	      choice = r.get('/radio/'+msg+'/uri')
	      if choice != None:
		  player.stop()
		  r.set('/radio/current',msg)
		  player.setUri(choice)
		  r.set('/radioPlaying','1')
		  player.play()
		  print 'Playing radio '+msg
      elif chan == '/airPlaying':
	  if msg == '1':
	      r.set('/airPlaying','1')
	      player.stop()
	      print 'Stop playing radio : AirPlay starts'
	  else:
	      r.set('/airPlaying','0')
	      if r.get('/radioPlaying') == '1':
		  player.play()
		  print 'Resume radio playing : AirPlay stops'

