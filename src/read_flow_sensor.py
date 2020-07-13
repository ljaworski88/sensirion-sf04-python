#!/usr/bin/env python3

import flow_sensor
import smbus2
from time import sleep

bus = smbus2.SMBus(1)

flow_sensor.reset_sensor(bus)

sleep(0.05)

while(True):
    reading, _ = flow_sensor.read_sensor(bus)
    print('flow reading: {}'.format(reading))
    print('crc byte: {}'.format(_))
