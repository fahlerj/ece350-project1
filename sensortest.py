### code below written to verify installation and implementation of DHT library
### DHT sensor allows reading of humidity and temperature simultaneously


import Adafruit_DHT as dht
import time
import RPi.GPIO as GPIO

DHTsensor = dht.DHT11 # sensor type
DHTpin = 4 # assigns GPIO pin (s pin on DHT sensor)

ht= dht.read(DHTsensor, DHTpin)

print(ht[0])

