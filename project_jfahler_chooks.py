#!/usr/bin/env python3
import smbus
import time
from time import sleep
import os
import Adafruit_DHT as dht
import RPi.GPIO as GPIO


### Assign GPIO pins for each component
DHTsensor = dht.DHT11 # sensor type
DHTpin = 4 # assigns GPIO pin (s pin on DHT sensor)

### Assign GPIO pins for each component
servopin = 31
GPIO.setmode(GPIO.BOARD)
GPIO.setup(servopin, GPIO.OUT)
servo = GPIO.PWM(servopin, 50)
servo.start(0)

# Reads temperature from all sensors found in /sys/bus/w1/devices/
# starting with "28-...
def readSensors():
  h, t = dht.read_retry(DHTsensor, DHTpin)

  if h is not None and t is not None:
    return h, t
  else:
    h = t = 0
    return h, t

### SG90 servo takes numerical temperature input and displays
def servocontrol(temperature, humidity = 0):

  ## We're limiting the temperature band between 0-360F for the purposes of mapping to dial
  angle = temperature
  ## set duty cycle to 360 degrees based on dial for temperature readout
  duty_cycle = 2.5 + 10 * angle / 360
  servo.ChangeDutyCycle(duty_cycle)
  sleep(.1)



def delay(time):
  sleep(time/1000.0)

def delayMicroseconds(time):
  sleep(time/1000000.0)

class Screen():

  enable_mask = 1<<2
  rw_mask = 1<<1
  rs_mask = 1<<0
  backlight_mask = 1<<3

  data_mask = 0x00

  def __init__(self, cols = 16, rows = 2, addr=0x27, bus=1):
    self.cols = cols
    self.rows = rows
    self.bus_num = bus
    self.bus = smbus.SMBus(self.bus_num)
    self.addr = addr
    self.display_init()

  def enable_backlight(self):
    self.data_mask = self.data_mask|self.backlight_mask

  def disable_backlight(self):
    self.data_mask = self.data_mask& ~self.backlight_mask

  def display_data(self, *args):
    self.clear()
    for line, arg in enumerate(args):
      self.cursorTo(line, 0)
      self.println(arg[:self.cols].ljust(self.cols))

  def cursorTo(self, row, col):
    offsets = [0x00, 0x40, 0x14, 0x54]
    self.command(0x80|(offsets[row]+col))

  def clear(self):
    self.command(0x10)

  def println(self, line):
    for char in line:
      self.print_char(char)

  def print_char(self, char):
    char_code = ord(char)
    self.send(char_code, self.rs_mask)

  def display_init(self):
    delay(1.0)
    self.write4bits(0x30)
    delay(4.5)
    self.write4bits(0x30)
    delay(4.5)
    self.write4bits(0x30)
    delay(0.15)
    self.write4bits(0x20)
    self.command(0x20|0x08)
    self.command(0x04|0x08, delay=80.0)
    self.clear()
    self.command(0x04|0x02)
    delay(3)

  def command(self, value, delay = 50.0):
    self.send(value, 0)
    delayMicroseconds(delay)

  def send(self, data, mode):
    self.write4bits((data & 0xF0)|mode)
    self.write4bits((data << 4)|mode)

  def write4bits(self, value):
    value = value & ~self.enable_mask
    self.expanderWrite(value)
    self.expanderWrite(value | self.enable_mask)
    self.expanderWrite(value)

  def expanderWrite(self, data):
    self.bus.write_byte_data(self.addr, 0, data|self.data_mask)

if __name__ == "__main__":
    screen = Screen(bus=1, addr=0x27, cols=16, rows=2)
    screen.enable_backlight()

    fileWrite = 'dataStore.log'

    while True:
      fileOut = open(fileWrite, 'a') # open file for reading on loop start
      humd, temp = readSensors()
      curr_time  = time.ctime()
      tempFar    = (temp * 9 / 5) + 32
      Tprint     = "Temp: {:.2f}F".format(tempFar)
      Hprint     = "Humidity: {:.1f}%".format(humd)
      screen.display_data(Tprint, Hprint)
      servocontrol(tempFar)

      # write the sensor readings to a log file with a timestamp
      fileOut.write(curr_time + " - " + str(Tprint + ", " + Hprint + "\n"))
      # flush the contents of the buffer to the file (so it can be followed during program exec)
      fileOut.close()
      sleep(1)
