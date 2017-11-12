# PROJ 4 CODE
#!/usr/bin/python

import socket
import urlparse
import re
import os
from HTMLParser import HTMLParser

PORT = 80
ROOT = "fring.ccs.neu.edu"
CSRF = ""
session = ""
pages_visited = []
pages_to_visit = []

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
  def handle_starttag(self, tag, attrs):
    if tag == 'input':
      newkeys = [i[0] for i in attrs]
      try:
        indexOfName = newkeys.index('name')
        if indexOfName > 0:
          if attrs[indexOfName][1] == 'csrfmiddlewaretoken':
            token = attrs[newkeys.index('value')][1]
            self.csrf = token
      except ValueError:
        pass
    elif tag == 'a':
      newkeys = [i[0] for i in attrs]
      try:
        hrefIndex = newkeys.index('href')
        if hrefIndex > 0:
          pages_to_visit.append(attrs[hrefIndex][1])
      except Error as E:
        pass

  def handle_endtag(self, tag):
    pass

  def handle_data(self, data):
    pass


# instantiate the parser and fed it some HTML
parser = MyHTMLParser()

socket.setdefaulttimeout = 0.50
os.environ['no_proxy'] = '127.0.0.1,localhost'
linkRegex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
CRLF = "\r\n\r\n"
NL = "\r\n"
CSRF = ""

def spider():
  global ROOT, PORT
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((ROOT, PORT))
  visited = []
  destinations = []

  destinations = logon("http://fring.ccs.neu.edu/accounts/login/?next=/fakebook/", s)

  s.shutdown(1)
  s.close()


def request(type, url, contentType = None, contentLength = None, cookies = {}, data = {}):
  r = "%s %s HTTP/1.1\r\nhost: fring.ccs.neu.edu\r\n" % (type, url)
  if contentType:
    r = r + "Content-Type: " + contentType + "\r\n"
  if contentLength:
    r = r + "Content-Length: " + str(contentLength) + "\r\n"
  if not len(cookies.keys()) == 0:
    r = r + "Cookie: "
    for key in cookies.keys():
      r = r + key + "=" + cookies[key] + "; "
    r = r[:-2] + "\r\n"
  if data:
    r = r + "\r\n" + data
  r = r + "\r\n\r\n"
  print r
  return r

def logon(url, s):
  global ROOT, CSRF
  url = urlparse.urlparse(url)
  path = url.path
  req = request("GET", path)
  s.send(req)
  data = s.recv(1000000)
  parser.feed(data)
  get_cookies(data)
  cookies = {'csrftoken': CSRF, 'sessionid': str(session)}
  login_data = 'csrfmiddlewaretoken='+CSRF+'&next=%2Ffakebook%2F&username=1732187&password=8ZUTZ78U'
  req = request("POST", path, 'application/x-www-form-urlencoded', str(len(login_data)), cookies, login_data)
  s.send(req)
  data = s.recv(1000000)
  print data
  return handle(data, s)

def crawl(url, s, abs=False):
  global ROOT, CSRF
  url = urlparse.urlparse(url)
  cookies = {'csrftoken': CSRF, 'sessionid': str(session)}
  req = request('GET', url.path, cookies=cookies)
  s.send(req)
  data = s.recv(1000000)
  print data
  return handle(data, s)

def get_cookies(data):
  global CSRF, session
  my_regex = r"sessionid=(.*); e"
  matches = re.search(my_regex, data)
  if matches:
    session = matches.group(1)
  if parser.csrf:
    CSRF = parser.csrf

def handle(data, s):
  my_regex = r"HTTP/1\.1 (\d*)"
  matches = re.search(my_regex, data)
  code = matches.group(1)

  if code == '302':
    return handle_found(data, s)
  elif code == "200":
    print data


def handle_found(data, s):
  my_regex = r"Location: (http://fring\.ccs\.neu\.edu.*)\r"
  matches = re.search(my_regex, data)
  crawl(matches.group(1), s)

spider()