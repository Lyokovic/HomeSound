#! /usr/bin/python2
# -*- coding:utf-8 -*-

from flask import Flask, Response, request, render_template
#from gevent.wsgi import WSGIServer
#from flask_bootstrap import Bootstrap
import redis
import json
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

    idSpeakers = [x.split('/')[2] for x in r.keys('/device/*/name')]
    speakers=[]
    for speaker in idSpeakers:
        name = r.get('/device/'+speaker+'/name')
        speakers.append((speaker,name))

    return render_template('homeJS.template', playing=playing,stations=stations,speakers=speakers,current=current)

@app.route("/editRadios")
def editRadios():
    # Get GET parameters
    action = request.args.get('action')
    id = request.args.get('id')
    name = request.args.get('name')
    uri = request.args.get('uri')
    form = request.args.get('form')

    ret = '-1'
    if action != None:
        if action == 'delete':
            if id != None:
                r.publish('/radio/delete',id)
                ret = id
        elif action == 'add':
            if name != None and uri != None:
                message = json.dumps({'name':name,'uri':uri})
                r.publish('/radio/add',message)
                ret = '0'
            else:
                ret = '-1 Name and/or URL parameter missing'

        if form == None:
            return ret

        time.sleep(0.2)

    # Get current station and station list
    current = r.get('/radio/current')
    if current == None:
        current = 0
    idStations = [x.split('/')[2] for x in r.keys('/radio/*/name') if x != 'current']
    idStations.sort()
    stations=[]
    for station in idStations:
        stationName = r.get('/radio/'+station+'/name')
        stations.append((station,stationName))

    return render_template('editRadios.template', stations=stations,current=current)

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

@app.route("/speakerReq")
def speakerReq():
    action = request.args.get('action')
    speaker = request.args.get('speaker')
    if (speaker != None):
        if action == None:
            r.publish('/device/toogle',speaker)
        elif action == 'enable':
            r.publish('/device/enable',speaker)
        else:
            r.publish('/device/disable',speaker)
        time.sleep(0.1)

    state = r.get('/device/'+speaker+'/enabled');
    if state != None:
        return json.dumps({'speaker':speaker,'state':state})
    else:
        return json.dumps({speaker:'-1'})

@app.route("/statusReq")
def statusReq():
    playing = getPlaying()
    current = r.get('/radio/current')
    idSpeakers = [x.split('/')[2] for x in r.keys('/device/*/enabled')]
    speakers=[]
    for speaker in idSpeakers:
        state = r.get('/device/'+speaker+'/enabled')
        speakers.append({'speaker':speaker,'state':state})
    return json.dumps({'playing':playing,'current':current,'speakers':speakers})

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
                    yield 'data: %s\n\n' % statusReq()
        except GeneratorExit:
            print "Déconnecté"
            pubsub.unsubscribe()
            return

    return Response(event_stream(),  mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080, threaded=True)

