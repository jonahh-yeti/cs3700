import socket
import ssl
import sys

# script takes 4 arguments passed from bash
# part should just be a number
# use_ssl is either 'true' or 'false'
# host is the hostname to connect to
# nuid is the nuid of the student
port = int(sys.argv[1])
use_ssl = sys.argv[2]
host = sys.argv[3]
nuid = sys.argv[4]

s = socket.socket()

# wraps the socket obnject with SSL if the flag was set
if use_ssl == "true":
  s = ssl.wrap_socket(s, keyfile='domain.key', certfile='domain.crt')

s.connect((host, port))

# Send the hello message and take the first response
s.sendall("cs3700fall2017 HELLO " + str(nuid) +"\n")
msg = s.recv(256)

# Autosolve messages until a BYE is found
while (msg.find("BYE") == -1):
  if msg.startswith("cs3700fall2017 STATUS"):
    try:
      ans = eval(msg[22:])
    except SyntaxError as error:
      print "Could not evaluate " + msg[22:] + ", caught error: " + repr(error) + ".  Exiting."
      sys.exit()
    s.sendall("cs3700fall2017 " + str(ans) + "\n")
    msg = s.recv(256)
  else:
    print "Response was not a STATUS message or a BYE message.  Exiting."
    sys.exit()
# print the secret
print msg[15:msg.find("BYE")-1]
