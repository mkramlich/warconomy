#!/usr/bin/env python2.5

from twisted.internet import reactor
import time

def hello(): print time.time()

def stop():
    print 'stopping'
    reactor.stop()

reactor.callLater(1, hello)
reactor.callLater(5,hello)
reactor.callLater(6,stop)

reactor.run()
