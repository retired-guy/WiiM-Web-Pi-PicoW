import rp2
import network
import ubinascii
import time
import socket
import json

import wiimclient
from secrets import secrets

# Set country to avoid possible errors
rp2.country('US')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# If you need to disable powersaving mode
# wlan.config(pm = 0xa11140)

# See the MAC address in the wireless chip OTP
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print('mac = ' + mac)

# Load login data from different file for safety reasons
ssid = secrets['ssid']
pw = secrets['pw']
wiimip = secrets['wiimip']

wlan.connect(ssid, pw)

# Wait for connection with 10 second timeout
timeout = 10
while timeout > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    timeout -= 1
    print('Waiting for connection...')
    time.sleep(1)

# Handle connection error
# Error meanings
# 0  Link Down
# 1  Link Join
# 2  Link NoIp
# 3  Link Up
# -1 Link Fail
# -2 Link NoNet
# -3 Link BadAuth

wlan_status = wlan.status()

if wlan_status != 3:
    raise RuntimeError('Wi-Fi connection failed')
else:
    print('Connected')
    status = wlan.ifconfig()
    print('ip = ' + status[0])
    
# HTTP server with socket
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('Listening on', addr)

# Listen for connections
while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        r = cl.recv(1024)
        
        r = str(r)
        action = r.find('?action')
        if action > -1:
            dict = wiimclient.getWiimData(wiimip)
            response = str.encode(json.dumps(dict))
            cl.send('HTTP/1.0 200 OK\r\nContent-type: text/json\r\n\r\n')
            cl.send(response)
            cl.close()
            
        if action == -1:
            try:
              path = r.split("GET ")[1]
              path = path.split(" HTTP")[0]
                
              if path == "/":
                  path = "/index.html"
            
              print("path:", path)
              ct = "text/html"

              if path == "/favicon.ico":
                  pass
              else:
                cl.send(f'HTTP/1.0 200 OK\r\nContent-type: {ct}\r\n\r\n')
                with open(path,'rb') as file:
                    sendfile = file.read()
                    
                cl.sendall(sendfile)    
                cl.close()
            except Exception as e:
              print(e)
        
    except OSError as e:
        cl.close()
        print('Connection closed')
