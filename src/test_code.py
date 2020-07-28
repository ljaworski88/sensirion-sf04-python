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

    try:
        product_name, product_serial, name_crc_result, serial_crc_result = read_product_info(bus, True)
        print('Product Name: {}'.format(product_name))
        print('Serial Number: {}'.format(product_serial))
        print('Product name CRC passed: {}'.format(name_crc_result))
        print('Product serial CRC passed: {}'.format(serial_crc_result))
    except Exception as e:
        print('Failed retrieving product_name')
        print('error encountered is:')
        print(e)


    try:
        user_reg_val, user_reg_crc, user_crc_result = read_user_reg(bus, True)
        print('User Register Value: {0: b}'.format(user_reg_val.value))
        print('User Register CRC Value: {0: b}'.format(user_reg_crc.value))
        print('User Register CRC Result: {}'.format(user_crc_result))
    except Exception as e:
        print('Failed to read the user register')
        print('error encountered is:')
        print(e)

    try:
        adv_reg_val, adv_reg_crc, adv_crc_result = read_adv_reg(bus, True)
        print('Advance User Register Value: {0: b}'.format(adv_reg_val.value))
        print('Advance User Register CRC Value: {0: b}'.format(adv_reg_crc.value))
        print('Advance User Register CRC Result: {}'.format(adv_crc_result))
    except Exception as e:
        print('Failed to read the advanced register')
        print('error encountered is:')
        print(e)

    for x in range(9,17):
        try:
            function_result = set_resolution(bus, x, True)
            print('Set resolution success: {}'.format(function_result))
        except Exception as e:
            print('Failed to set the resoltution')
            print('error encountered is:')
            print(e)

        try:
            adv_reg_val, adv_reg_crc, adv_crc_result = read_adv_reg(bus, True)
            print('Advance User Register Value: {0: b}'.format(adv_reg_val.value))
            print('Advance User Register CRC Value: {0: b}'.format(adv_reg_cr.valuec))
            print('Advance User Register CRC Result: {}'.format(adv_crc_result))
        except Exception as e:
            print('Failed to read the advanced register')
            print('error encountered is:')
            print(e)

    for x in range(0, 5):
        try:
            function_result = set_calibration_field(bus, x, True)
            print('Set calibration field success: {}'.format(function_result))
        except Exception as e:
            print('Failed retrieving product_name')
            print('error encountered is:')
            print(e)

        try:
            user_reg_val, user_reg_crc, user_crc_result = read_user_reg(bus, True)
            print('User Register Value: {0: b}'.format(user_reg_val.value))
            print('User Register CRC Value: {0: b}'.format(user_reg_crc.value))
            print('User Register CRC Result: {}'.format(user_crc_result))
        except Exception as e:
            print('Failed to read the user register')
            print('error encountered is:')
            print(e)

        try:
            scale_factor, units, scale_crc, unit_crc = read_scale_and_unit(bus, True)
            print('Scale factor is: {}'.format(scale_factor.value))
            print('Units are: {}'.format(units))
            print('Scale factor CRC result: {}'.format(scale_crc))
        except Exception as e:
            print('Failed to read the scale factor and unit')
            print('error encountered is:')
            print(e)

        for reading_type in ['flow', 'temp', 'vdd']:
            try:
                set_read_data(bus, reading_data)
            except Exception as e:
                print('Failed to set the sensor to read mode')
                print('error encountered is:')
                print(e)

            try:
                raw_data, data_crc, data_crc_result = read_raw_data(bus, True)
            except Exception as e:
                print('Failed retrieving the data')
                print('error encountered is:')
                print(e)

            try:
                scaled_data = scale_reading(raw_data.value, scale_factor.value)
                print('Raw {0} reading: {1}'.format(reading_type, raw_data.value))
                print('Raw data CRC: {}'.format(data_crc.value))
                print('CRC result: {}'.format(data_crc_result))
                print('Scaled {0} reading: {1} {2}'.format(reading_type, scaled_data, units))
            except Exception as e:
                print('Failed scaling the result')
                print('error encountered is:')
                print(e)
