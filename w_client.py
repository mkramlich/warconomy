#!/usr/bin/env python2.5

import sys
from twisted.internet import stdio, reactor
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

#out_msg_queue = []

class ConsoleClient(LineReceiver):
    delimiter = '\n'

    def connectionMade(self):
        self.sendLine("co client conn made (cl)")

    def lineReceived(self, line):
        if not line: return
        #self.sendLine("co client line recvd: '%s'" % line)
        if line == 'q':
            reactor.stop()
        #out_msg_queue.append(line)
        server_client.send_to_server(line)

    def connectionLost(self, reason):
        #self.sendLine('client conn lost: %s' % reason.getErrorMessage())
        reactor.stop()

    def connectionFailed(self, reason):
        #self.sendLine('client conn failed: %s' % reason.getErrorMessage())
        reactor.stop()

player_id = 0

class ServerClient(LineReceiver):
    def connectionMade(self):
        print 'sv client conn made'
        print 'sv client logging in as player_id %i' % player_id
        self.sendLine('login %i' % player_id)
        self.sendLine('ui')

    def connectionLost(self, reason):
        print 'sv client conn lost: %s' % reason
        #reactor.stop()

    def lineReceived(self, line):
        #print "sv client line recvd: '%s'" % line
        print line.strip()

    def send_to_server(self, msg):
        self.sendLine(msg)

server_client = None

class ServerClientFactory(ClientFactory):
    protocol = ServerClient

    def startedConnecting(self, connector):
        print 'scf started connecting (%s)' % connector

    def clientConnectionLost(self, connector, reason):
        print 'scf client conn lost: %s' % reason.getErrorMessage()

    def clientConnectionFailed(self, connector, reason):
        print 'scf client conn failed: %s' % reason.getErrorMessage()

    def buildProtocol(self, addr):
        global server_client
        server_client = self.protocol()
        return server_client

def main():
    global player_id
    print 'Warconomy client'
    if len(sys.argv) > 1:
        player_id = int(sys.argv[1])
    stdio.StandardIO(ConsoleClient())
    reactor.connectTCP('localhost',8007,ServerClientFactory())
    reactor.run()
    print 'exiting main()'

if __name__ == "__main__":
    main()
