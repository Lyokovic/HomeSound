#! /usr/bin/python2
# -*- coding:utf-8 -*-

from flask import Flask, request, render_template
from flask_bootstrap import Bootstrap
import redis
import time

app = Flask(__name__)
Bootstrap(app)

r = redis.StrictRedis()

@app.route("/")
def hello():
	action = request.args.get('action')
	radio = request.args.get('radio')
	if action != None:
		if action == 'play':
			if radio == None:
				radio = ''
			r.publish('/radioPlay',radio)
		elif action == 'stop':
			r.publish('/radioPlay','-1')

	time.sleep(0.2)
	playing = r.get('/radioPlaying')

	idStations = [x.split('/')[2] for x in r.keys('/radio/*/name') if x != 'current']
	stations=[]
	for station in idStations:
	    name = r.get('/radio/'+station+'/name')
	    if r.get('/radio/current') == station:
		state = '1'
	    else:
		state = '0'
	    stations.append((station,name,state))

	return render_template('page.template', playing=playing,stations=stations)

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8080)
