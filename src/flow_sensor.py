#!/usr/bin/env python3

from smbus2 import SMBus, i2c_msg
from time import sleep

__author__ = 'Lukas Jaworski'
__version__ = '0.1.0'

_sensor_address = 0x40

_user_reg_w = 0xE2
_user_reg_r = 0xE3
_adv_user_reg_w = 0xE4
_adv_user_reg_r = 0xE5
_read_only_reg = 0xE9
_trig_flow_read = 0xF1
_trig_temp_read = 0xF3
_trig_vdd_read = 0xF5
_read_eeprom = 0xFA
_soft_rest = 0xFE

def read_sensor(i2c_bus):
    '''
    Reads the SLG-0150 Sensirion sensor and returns a reading and a CRC error
    checksum byte
    ---------------------------------------------------------------------------
    input: None
    output: (Reading, CRC) - type (int, int)
    '''
    flow_data = i2c_bus.read_i2c_block_data(_sensor_address, _trig_flow_read, 3)
    flow_reading = (flow_data[0] << 8 | flow_data[1])
    crc_bit = flow_data[2]
    return (flow_reading, crc_bit)

def check_CRC(reading, crc_byte):
    '''
    Checks the reading runs it through a CRC8 checksum function to ensure data
    integrity.
    ---------------------------------------------------------------------------
    input: reading, crc_byte
    output: checksum_result - type bool
    '''
    pass

def reset_sensor(i2c_bus, soft=True):
    '''
    Perform a soft reset of the sensor.
    ---------------------------------------------------------------------------
    input soft - type: bool
    output: None
    '''
    if soft:
        i2c_bus.write_byte(_sensor_address, _soft_rest)
        # print('soft reset result: {}'.format(result))


if __name__ == '__main__':
    with SMBus(1) as bus:
    # bus = smbus2.SMBus(1)
        bus.write_byte(_sensor_address, _soft_rest)
        print("Sensor reset!")

        sleep(0.5)

        while(True):
            bus.write_byte(_sensor_address, _trig_flow_read)
            # write = i2c_msg.write(_sensor_address, _trig_flow_read)
            read = i2c_msg.read(_sensor_address, 3)
            flow_data = bus.i2c_rdwr(read)
            # flow_data = bus.read_i2c_block_data(_sensor_address, _trig_flow_read, 3)
            print(flow_data)
            # reading, _ = read_sensor(bus)
            # print('flow reading: {}'.format(reading))
            # print('crc byte: {}'.format(_))
