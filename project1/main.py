import socket
import ssl
import sys

port = int(sys.argv[1])
use_ssl = sys.argv[2]
host = sys.argv[3]
nuid = sys.argv[4]

s = socket.socket()

if use_ssl == "true":
  s = ssl.wrap_socket(s, keyfile='domain.key', certfile='domain.crt')

s.connect((host, port))

s.sendall("cs3700fall2017 HELLO " + str(nuid) +"\n")
msg = s.recv(256)

while (msg.find("BYE") == -1):
  print msg
  ans = eval(msg[22:])
  s.sendall("cs3700fall2017 " + str(ans) + "\n")
  msg = s.recv(256)
print msg[15:msg.find("BYE")-1]
