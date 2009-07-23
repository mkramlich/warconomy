#!/usr/bin/env python2.5

from twisted.internet import reactor

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory

class Answer(LineReceiver):

    answers = {'color': 'green', None : 'unknown'}

    def connectionMade(self):
        print 'server got conn'

    def connectionLost(self, reason):
        print 'server lost conn: %s' % reason

    def lineReceived(self, line):
        print "server line recv: '%s'" % line
        resp = "hey! we got: '%s'\n" % line
        print "server responding: '%s'" % resp
        self.transport.write(resp)

factory = Factory()
factory.protocol = Answer
reactor.listenTCP(8007, factory)
reactor.run()
