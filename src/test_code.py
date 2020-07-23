#!/usr/bin/env python3

from smbus2 import SMBus, i2c_msg
from time import sleep
from ctypes import *
from sf04_sensor import *


# Some tests to check the function of this library
with SMBus(3) as bus:
    reset_sensor(bus)
    print("Sensor reset!")
    sleep(0.5)

    product_name, product_serial, name_crc_result, serial_crc_result = read_product_info(bus, True)
    print('Product Name: {}'.format(product_name))
    print('Serial Number: {}'.format(product_serial))
    print('Product name CRC passed: {}'.format(name_crc_result))
    print('Product serial CRC passed: {}'.format(serial_crc_result))

    user_reg_val, user_reg_crc, user_crc_result = read_user_reg(bus, True)
    print('User Register Value: {0: b}'.format(user_reg_val.value))
    print('User Register CRC Value: {0: b}'.format(user_reg_crc.value))
    print('User Register CRC Result: {}'.format(user_crc_result))

    adv_reg_val, adv_reg_crc, adv_crc_result = read_adv_reg(bus, True)
    print('Advance User Register Value: {0: b}'.format(adv_reg_val.value))
    print('Advance User Register CRC Value: {0: b}'.format(adv_reg_crc.value))
    print('Advance User Register CRC Result: {}'.format(adv_crc_result))

    for x in range(9,17):
        function_result = set_resolution(bus, x, True)
        print('Set resolution success: {}'.format(function_result))
        adv_reg_val, adv_reg_crc, adv_crc_result = read_adv_reg(bus, True)
        print('Advance User Register Value: {0: b}'.format(adv_reg_val.value))
        print('Advance User Register CRC Value: {0: b}'.format(adv_reg_cr.valuec))
        print('Advance User Register CRC Result: {}'.format(adv_crc_result))

    for x in range(0, 5):
        function_result = set_calibration_field(bus, x, True)
        print('Set calibration field success: {}'.format(function_result))
        user_reg_val, user_reg_crc, user_crc_result = read_user_reg(bus, True)
        print('User Register Value: {0: b}'.format(user_reg_val.value))
        print('User Register CRC Value: {0: b}'.format(user_reg_crc.value))
        print('User Register CRC Result: {}'.format(user_crc_result))
        scale_factor, units, scale_crc, unit_crc = read_scale_and_unit(bus, True)
        print('Scale factor is: {}'.format(scale_factor.value))
        print('Units are: {}'.format(units))
        print('Scale factor CRC result: {}'.format(scale_crc))
        for reading_type in ['flow', 'temp', 'vdd']:
            set_read_data(bus, reading_data)
            raw_data, data_crc, data_crc_result = read_raw_data(bus, True)
            scaled_data = scale_reading(raw_data, scale_factor)
            print('Raw {0} reading: {1}'.format(reading_type, raw_data.value))
            print('Raw data CRC: {}'.format(data_crc.value))
            print('CRC result: {}'.format(data_crc_result))
            print('Scaled {0} reading: {1} {2}'.format(reading_type, scaled_data, units))
