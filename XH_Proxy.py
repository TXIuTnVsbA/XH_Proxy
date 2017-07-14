#coding=utf8
import socket, select
import sys
import thread
#import ConfigParser
from multiprocessing import Process

class Proxy:
    def __init__(self, soc):
        self.client, _ = soc.accept()
        self.ip='111.13.7.120'
        self.port=80
        #self.target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.target = None
        self.BUFSIZE = 1024 * 4
        self.method = None

    def header(self,request):
        if not request:
            return
        #print request
        list = request.split('\n')
        Line1 = list[0]
        Line2 = list[1]
        Line3 = list[2]
        line = Line1.split()
        self.method = line[0]
        allhead = request.replace('X-Online-Host:','Host:')
        allhead = allhead.replace(Line2 + '\n', '')
        allhead = allhead.replace(Line3 + '\n','')
        #print allhead
        return allhead

    def Method(self, request):
        try:
            self.target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.target.connect((self.ip, self.port))
            self.target.send(request)
            self.packet()
        except:
            self.client.close()

    def packet(self, timeout=1):
        inputs = [self.client, self.target]
        while True:
            readable, _, errs = select.select(inputs, [], inputs, timeout)
            if errs:
                break
            for packet in readable:
                try:
                    data = packet.recv(self.BUFSIZE)
                    if packet is self.client:
                        if self.method in ['GET', 'POST', 'PUT', "DELETE", 'HAVE']:
                            data = self.header(data)
                            self.target.send(data)
                        elif self.method == 'CONNECT':
                            self.target.send(data)
                    elif packet is self.target:
                        self.client.send(data)
                except:
                    break
        self.client.close()
        self.target.close()

    def run(self):
        request = self.client.recv(self.BUFSIZE)
        request = self.header(request)
        if request:
            self.Method(request)


if __name__ == '__main__':
    from multiprocessing import Process
    host = '127.0.0.1'
    port = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    try:
        while True:
            thread.start_new_thread(Proxy(server).run, ())
    except KeyboardInterrupt:
        server.close()
        sys.exit(0)
