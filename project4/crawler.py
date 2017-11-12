# PROJ 4 CODE
# !/usr/bin/python

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
found_headers = []


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.readData = False

  def handle_starttag(self, tag, attrs):
    global pages_to_visit, pages_visited, found_headers
    if tag == 'a':
      newkeys = [i[0] for i in attrs]
      try:
        hrefIndex = newkeys.index('href')
        if hrefIndex >= 0:
          i = attrs[hrefIndex][1]
          try:
            pages_visited.index(i)
          except:
            if re.match(r"(/fakebook.*/)", i):
              pages_to_visit.append(i)
      except Error as E:
        pass
    elif tag == 'h2':
      newkeys = [i[0] for i in attrs]
      try:
        classIndex = newkeys.index('class')
        if classIndex >= 0:
          i = attrs[classIndex][1]
          if i == 'secret_flag':
            self.readData = True
      except:
        pass

  def handle_data(self, data):
    global found_headers
    if self.readData:
      self.readData = False
      print "FOUND READ DATA IS TRUE, PRINTING DATA"
      print "FOUND : " + str(data)
      flag_regex = r"FLAG: (.*)"
      matches = re.search(flag_regex, data)
      found_headers.append(matches.group(1))


# instantiate the parser and fed it some HTML
parser = MyHTMLParser()

socket.setdefaulttimeout = 10
os.environ['no_proxy'] = '127.0.0.1,localhost'
linkRegex = re.compile('<a\s*href=[\'|"](.*?)[\'"].*?>')
CRLF = "\r\n\r\n"
NL = "\r\n"
CSRF = ""


def spider():
  global ROOT, PORT, pages_to_visit, pages_visited, found_headers
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((ROOT, PORT))

  logon("http://fring.ccs.neu.edu/accounts/login/?next=/fakebook/", s)
  count = 1
  while pages_to_visit and len(found_headers) < 5:
    if count % 3 == 0:
      try:
        s.shutdown(1)
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ROOT, PORT))
      except:
        continue
    print "RUNNING: " + str(count)
    count += 1
    crawl('http://fring.ccs.neu.edu' + pages_to_visit[0], s)

  print str(found_headers)

  s.shutdown(1)
  s.close()


def request(type, url, contentType=None, contentLength=None, cookies={}, data={}):
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
  return r


def logon(url, s):
  global ROOT, CSRF
  url = urlparse.urlparse(url)
  path = url.path
  req = request("GET", path)
  s.send(req)
  data = s.recv(1000000)
  get_cookies(data)
  cookies = {'csrftoken': CSRF, 'sessionid': str(session)}
  login_data = 'csrfmiddlewaretoken=' + CSRF + '&next=%2Ffakebook%2F&username=1732187&password=8ZUTZ78U'
  req = request("POST", path, 'application/x-www-form-urlencoded', str(len(login_data)), cookies, login_data)
  s.send(req)
  data = s.recv(1000000)
  get_cookies(data)
  return handle(data, s, path)


def crawl(url, s):
  global ROOT, CSRF
  url = urlparse.urlparse(url)
  cookies = {'csrftoken': CSRF, 'sessionid': str(session)}
  req = request('GET', url.path, cookies=cookies)
  s.send(req)
  data = s.recv(1000000)
  get_cookies(data)
  return handle(data, s, url.path)


def get_cookies(data):
  global CSRF, session
  session_regex = r"sessionid=(.*); e"
  session_matches = re.search(session_regex, data)
  if session_matches:
    session = session_matches.group(1)

  csrf_regex = r"csrftoken=(.*); e"
  csrf_matches = re.search(csrf_regex, data)
  if csrf_matches:
    CSRF = csrf_matches.group(1)


def handle(data, s, path):
  my_regex = r"HTTP/1\.1 (\d*)"
  matches = re.search(my_regex, data)
  try:
    code = matches.group(1)
    if code == '302' or code == "301":
      handle_found(data, s, path)
    elif code == "200":
      handle_ok(data, s, path)
    elif code == "500":
      handle_error(data, s, path)
    elif code == "403" or code == "404":
      abort_request(data, s, path)
  except AttributeError as E:
    pass


def abort_request(data, s, path):
  global pages_visited, pages_to_visit
  pages_visited.append(path)
  try:
    pages_to_visit.remove(path)
  except:
    pass


def handle_error(data, s, path):
  crawl('http://fring.ccs.neu.edu' + path, s)


def handle_ok(data, s, path):
  pages_visited.append(path)
  try:
    pages_to_visit.remove(path)
  except:
    pass
  print "FEEDING FROM: " + str(path)
  parser.feed(data)


def handle_found(data, s, path):
  global pages_visited, pages_to_visit
  pages_visited.append(path)
  try:
    pages_to_visit.remove(path)
  except:
    pass
  my_regex = r"Location: (http://fring\.ccs\.neu\.edu.*)\r"
  matches = re.search(my_regex, data)
  crawl(matches.group(1), s)


spider()
