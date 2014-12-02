#! /usr/bin/python2
# -*- coding:utf-8 -*-

import redis

r = redis.StrictRedis()

r.set('/radio/current','0')
r.set('/airPlaying','0')
r.set('/radioPlaying','0')
r.set('/device/gpioMode','bcm')

r.set('/radio/0/name','Europe 1')
r.set('/radio/0/uri','http://vipicecast.yacast.net/europe1')

r.set('/radio/1/name','RTL')
r.set('/radio/1/uri','http://streaming.radio.rtl.fr/rtl-1-44-96')

r.set('/radio/2/name','RTL 2')
r.set('/radio/2/uri','http://streaming.radio.rtl2.fr/rtl2-1-44-96')

r.set('/radio/5/name','France Inter')
r.set('/radio/5/uri','http://mp3.live.tv-radio.com/franceinter/all/franceinterhautdebit.mp3')

r.set('/device/0/name','Enceinte 1')
r.set('/device/0/audioPin','17')
r.set('/device/0/buttonPin','22')
r.set('/device/0/enabled','0')

r.set('/device/1/name','Enceinte 2')
r.set('/device/1/audioPin','18')
r.set('/device/1/buttonPin','23')
r.set('/device/1/enabled','0')
