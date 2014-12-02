#! /usr/bin/python2

import RPi.GPIO as gpio
import redis
import time

class Speakers:
    def __init__(self):
        self.r = redis.StrictRedis()

        gpioMode = self.r.get('/device/gpioMode')
        if gpioMode == 'bcm':
            gpio.setmode(gpio.BCM)
        elif gpioMode == 'board':
            gpio.setmode(gpio.BOARD)
        else:
            raise RuntimeError("Error initializing GPIO: can't fetch a valid GPIO mode")

        # Get tuples (buttonPin,audioPin,state) of available speakers then initialize and keep them
        self.speakers = [(x.split('/')[2],self.r.get('/device/'+x.split('/')[2]+'/buttonPin'), self.r.get('/device/'+x.split('/')[2]+'/audioPin'), self.r.get('/device/'+x.split('/')[2]+'/enabled')) for x in self.r.keys('/device/*/name')]
        for (id, buttonPin, audioPin, state) in self.speakers:
            gpio.setup(int(audioPin),gpio.OUT)
            gpio.output(int(audioPin),1-int(state))
            gpio.setup(int(buttonPin),gpio.IN, pull_up_down=gpio.PUD_UP)
            gpio.add_event_detect(int(buttonPin), gpio.RISING, callback=self.handleButton, bouncetime=200)

    def handleButton(self,pin):
        time.sleep(0.1)
        if not gpio.input(pin):
            #print "Button pin: "+str(pin)+" pressed"
            speaker = [id for (id,buttonPin,audioPin,oldState) in self.speakers if buttonPin == str(pin)][0]
            self.r.publish('/device/toogle',speaker)

    def enable(self,id):
        gpio.output(int(self.speakers[int(id)][2]),0)

    def disable(self,id):
        gpio.output(int(self.speakers[int(id)][2]),1)

def main():
    p = Speakers()
    act = False
    while True:
        raw_input('Press enter')
        if act :
            print 'Desactivate'
            p.disable('17')
            act = False
        else :
            print 'Activate'
            p.enable('17')
            act = True

if __name__ == '__main__':
    main()
