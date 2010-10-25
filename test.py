import socket

print socket.gethostbyname( socket.gethostname() )
print socket.gethostbyname( socket.getfqdn() )
print socket.getaddrinfo(socket.gethostname(), None)[0][4][0]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(('google.com', 80))
print s.getsockname()[0]

host, aliaslist, lan_ip = socket.gethostbyname_ex(socket.gethostname())
print host
print aliaslist
print lan_ip[0]

import urllib
print urllib.urlopen('http://www.whatismyip.com/automation/n09230945.asp').read()
