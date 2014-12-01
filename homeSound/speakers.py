#! /usr/bin/python2

import wiringpi2 as wiringpi
import redis

class Speakers:
    def __init__(self):
        self.r = redis.StrictRedis()

        wiringpi.wiringPiSetup()
        speakers = [x.split('/')[2] for x in self.r.keys('/device/*/audioPin')]
        for pin in speakers:
            wiringpi.pinMode(int(pin),1)
            wiringpi.digitalWrite(int(pin),1)


    def enable(self,id):
        wiringpi.digitalWrite(int(id),0)

    def disable(self,id):
        wiringpi.digitalWrite(int(id),1)

def main():
    p = Player()
    act = False
    while True:
        raw_input('Press enter')
        if act :
            print 'Desactivate'
            p.disable('0')
            act = False
        else :
            print 'Activate'
            p.enable('0')
            act = True

if __name__ == '__main__':
    main()
