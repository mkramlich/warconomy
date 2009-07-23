#!/usr/bin/env python2.5

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientCreator
from twisted.protocols.basic import LineReceiver

nl = LineReceiver.delimiter

class Klient(Protocol):
    def connectionMade(self):
        print 'client conn made'
        self.transport.write('yo'+nl)

    def connectionLost(self, reason):
        print 'client conn lost: %s' % reason
        reactor.stop()

    def dataReceived(self, data):
        print "client data recvd: '%s'" % data

def gotProtocol(p):
    print 'gotproto'
    reactor.callLater(3, p.transport.loseConnection)

c = ClientCreator(reactor, Klient)
c.connectTCP('localhost', 8007).addCallback(gotProtocol)
reactor.run()
