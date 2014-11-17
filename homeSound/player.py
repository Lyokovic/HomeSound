#! /usr/bin/python2

import pygst
pygst.require("0.10")
import gst
import redis

class Player:
	def __init__(self):
		self.player = gst.element_factory_make("playbin2", "self.player")
		fakesink = gst.element_factory_make("fakesink","fakesink")
		alsa = gst.element_factory_make("alsasink","sink")

		self.player.set_property("audio-sink",alsa)
		self.player.set_property("video-sink",fakesink)

	def setUri(self,uri):	
		print 'Setting uri : '+uri
		self.player.set_property("uri", uri)
	def play(self):
		self.player.set_state(gst.STATE_PLAYING)

	def stop(self):
		self.player.set_state(gst.STATE_READY)

def main():
	player = Player()
	player.play()

	r = redis.StrictRedis()
	ps = r.pubsub()
	ps.subscribe('player')

	for item in ps.listen():
		if item['data'] == 'play':
			print "Play !"
			player.play()
		elif item['data'] == 'stop':
			print "Stop !"
			player.stop()

if __name__ == '__main__':
	main()
