# PROJ 4 CODE
#!/usr/bin/python

import socket
import urlparse
import re
import os
from HTMLParser import HTMLParser


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'input':
            print attrs
            newkeys = [i[0] for i in attrs]
            print newkeys
            try:
                indexOfName = newkeys.index('name')
                if indexOfName > 0:
                    if attrs[indexOfName][1] == 'csrfmiddlewaretoken':
                        token = attrs[newkeys.index('value')][1]
                        print token
            except ValueError:
                print "whoops not found"

    def handle_endtag(self, tag):
        print "Encountered an end tag :", tag

    def handle_data(self, data):
        print "Encountered some data  :", data


# instantiate the parser and fed it some HTML
parser = MyHTMLParser()

socket.setdefaulttimeout = 0.50
os.environ['no_proxy'] = '127.0.0.1,localhost'
linkRegex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
CRLF = "\r\n\r\n"



def GET(url):
    url = urlparse.urlparse(url)
    print url
    path = url.path
    if path == "":
        path = "/"
    HOST = url.netloc  # The remote host
    PORT = 80          # The same port as used by the server
    # create an INET, STREAMing socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    """
    ***********************************************************************************
    * Note that the connect() operation is subject to the timeout setting,
    * and in general it is recommended to call settimeout() before calling connect()
    * or pass a timeout parameter to create_connection().
    * The system network stack may return a connection timeout error of its own
    * regardless of any Python socket timeout setting.
    ***********************************************************************************
    """
    s.settimeout(0.30)
    """
    **************************************************************************************
    * Avoid socket.error: [Errno 98] Address already in use exception
    * The SO_REUSEADDR flag tells the kernel to reuse a local socket in TIME_WAIT state,
    * without waiting for its natural timeout to expire.
    **************************************************************************************
    """
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #s.setblocking(0)
    s.connect((HOST, PORT))
    message = "GET %s?%s HTTP/1.1%shost: %s%s" % (path, url.query, '\r\n', HOST, CRLF)
    print url.path
    print url.params
    print url.query
    print url.fragment
    print message
    s.send(message)
    data = (s.recv(1000000))
    print data

    parser.feed(data)


    # https://docs.python.org/2/howto/sockets.html#disconnecting
    s.shutdown(1)
    s.close()
    print 'Received', repr(data)


GET('http://fring.ccs.neu.edu/accounts/login/?next=/fakebook/')
