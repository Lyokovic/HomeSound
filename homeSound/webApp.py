#! /usr/bin/python2
# -*- coding:utf-8 -*-

from flask import Flask, Response, request, render_template
#from gevent.wsgi import WSGIServer
#from flask_bootstrap import Bootstrap
import redis
import time

app = Flask(__name__)
#Bootstrap(app)

r = redis.StrictRedis()


@app.route("/")
def index():
    playing = getPlaying()
    current = r.get('/radio/current')
    if current == None:
        current = 0

    idStations = [x.split('/')[2] for x in r.keys('/radio/*/name') if x != 'current']
    stations=[]
    for station in idStations:
        name = r.get('/radio/'+station+'/name')
        stations.append((station,name))
    return render_template('homeJS.template', playing=playing,stations=stations,current=current)

@app.route("/playReq")
def playReq():
    action = request.args.get('action')
    if action != None:
        if action == 'play':
            r.publish('/radioPlay','')
        elif action == 'stop':
            r.publish('/radioPlay','-1')
        time.sleep(0.1)

    playing = getPlaying()

    return playing

@app.route("/stationReq")
def stationReq():
    radio = request.args.get('radio')
    if radio != None:
        r.publish('/radioPlay',radio)
        time.sleep(0.1)

    current = r.get('/radio/current');
    return current

def getPlaying():
    if (r.get('/radioPlaying') == '1'):
        if (r.get('/airPlaying') == '1'):
            return '2'
        return  '1'
    return '0'

@app.route("/stream")
def stream():
    def event_stream():
        pubsub = r.pubsub()
        pubsub.subscribe('/playing')
        try:
            for item in pubsub.listen():
                if item['type'] == 'message':
                    playing = item['data'];
                    yield 'data: %s\n\n' % playing
        except GeneratorExit:
            print "Déconnecté"
            pubsub.unsubscribe()
            return

    return Response(event_stream(),  mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080, threaded=True)

