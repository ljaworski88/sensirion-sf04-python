#!/usr/bin/env python3

from smbus2 import SMBus, i2c_msg
from time import sleep
from ctypes import *
import crc8

__author__ = 'Lukas Jaworski'
__version__ = '0.9.5'

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

def read_comms(i2c_bus, register, bytes_to_read):
    '''
    Reads the SF04 Sensirion sensor and returns the specified number of bytes
    ---------------------------------------------------------------------------
    input: i2c_bus, register, bytes_to_read - type: SMBus2 bus, int, int
    output: byte_list - type: list(c_uint8->len=bytes_to_read)
    '''
    i2c_bus.write_byte(_sensor_address, register)
    read = i2c_msg.read(_sensor_address, bytes_to_read)
    i2c_bus.i2c_rdwr(read)
    # Change the results to c types for more precise bit manipulations
    byte_list = [c_uint8(x) for x in list(read)]
    return byte_list

def read_user_reg(i2c_bus, crc_check=False):
    '''
    Reads the user register of the SF04 Sensirion sensor and returns the value
    of the register, as well as the crc byte and the result of any CRC check if
    it was run.
    ----------------------------------------------------------------------------
    input: i2c_bus, crc_check - type: SMBus2 bus, bool[=False]
    output: reg_val, crc_byte, crc_result - type: c_uint16, c_uint8, bool
    '''
    reg_value_list = read_comms(i2c_bus, _user_reg_r, 3)
    reg_val = c_uint16(reg_value_list[0].value << 8 | reg_value_list[1].value)
    crc_byte = reg_value_list[2]
    crc_result = None
    if crc_check:
        crc_result = check_CRC(reg_val, crc_byte)
    return (reg_val, crc_byte, crc_result)

def read_adv_reg(i2c_bus, crc_check=False):
    '''
    Reads the advanced user register of the SF04 Sensirion sensor and returns the
    value of the register, as well as the crc byte and the result of any CRC
    check if it was run.
    ----------------------------------------------------------------------------
    input: i2c_bus, crc_check - type: SMBus2 bus, bool[=False]
    output: reg_val, crc_byte, crc_result - type: c_uint16, c_uint8, bool
    '''
    reg_value_list = read_comms(i2c_bus, _adv_user_reg_r, 3)
    reg_val = c_uint16(reg_value_list[0].value << 8 | reg_value_list[1].value)
    crc_byte = reg_value_list[2]
    crc_result = None
    if crc_check:
        crc_result = check_CRC(reg_val, crc_byte)
    return (reg_val, crc_byte, crc_result)

def set_resolution(i2c_bus, bits=16, crc_check=False):
    '''
    Reads the advanced user register of the SF04 Sensirion sensor and then sets
    the resoltuion of the readings by writing to the advanced user register.
    Resolution must be between 9 and 16 bits.
    ----------------------------------------------------------------------------
    input: i2c_bus, bits, crc_check - type: SMBus2 bus, int[=16], bool[=False]
    output: reg_val, crc_byte, crc_result - type: c_uint16, c_uint8, bool
    '''
    if int(bits) > 16 or int(bits) < 9:
        raise ValueError('bits must be an integer between 9 and 16 inclusive.')
    old_reg_val, crc_byte, adv_crc_result = read_adv_reg(i2c_bus, crc_check)
    if adv_crc_result or adv_crc_result is None:
        bits = bits - 9
        # The resolution field sits on bits [11:9] of the advanced user register
        # a setting of 000 on those bits coresponds to 9 bit resolution while
        # a value of 111 corresponds to 16 bits
        new_reg_val = c_uint16((old_reg_val.value & 0xF1FF) | (int(bits) << 9))
        i2c_bus.write_word_data(_sensor_address, _adv_user_reg_w, new_reg_val.value)
    return adv_crc_result

def set_calibration_field(i2c_bus, setting=0, crc_check=False):
    '''
    Reads the user register of the SF04 Sensirion sensor and then sets
    the calibration field of the sensor by writing to the user register.
    Setting must be between 0 and 5 inclusive.
    ----------------------------------------------------------------------------
    input: i2c_bus, setting, crc_check - type: SMBus2 bus, int[=0], bool[=False]
    output: reg_val, crc_byte, crc_result - type: c_uint16, c_uint8, bool
    '''
    if int(setting) < 0 or int(setting) > 4:
        raise ValueError('setting must be an integer between 0 and 4 inclusive')
    old_reg_val, crc_byte, user_crc_result = read_user_reg(i2c_bus, crc_check)
    if user_crc_result or user_crc_result is None:
        # The calibration field sits on bits [6:4] of the user register
        # valid values sit between 0 and 4, or 000 and 100 in binary
        new_reg_val = c_uint16((old_reg_val.value & 0xFF8F) | (int(setting) << 4))
        i2c_bus.write_word_data(_sensor_address, _user_reg_w, new_reg_val.value)
    return user_crc_result

def set_read_data(i2c_bus, source='flow'):
    '''
    Puts the SF04 sensor into measurement mode. Until another instruction is
    given the SF04 sensor will respond to all I2C read transactions by returning
    a max of 3 bytes, the first two are the sensor reading and the third is a
    crc8 checksum byte.
    ----------------------------------------------------------------------------
    input: i2c_bus, source - type: SMBus2 bus, string[='flow'{,'temp','vdd'}]
    output: None

    '''
    sources_dict = {'flow': _trig_flow_read,
                    'temp': _trig_temp_read,
                    'vdd' : _trig_vdd_read}
    i2c_bus.write_byte(_sensor_address, sources_dict[source])

def read_raw_data(i2c_bus, crc_check=False):
    '''
    Reads the SF04 sensor and returns a reading and a crc8 checksum byte and
    checksum result.
    ---------------------------------------------------------------------------
    input: i2c_bus, crc_check - type: SMBus2 bus, bool[=False]
    output: raw_flow_reading, crc_byte, crc_result - type: c_uint16, c_uint8, bool
    '''
    read = i2c_msg.read(_sensor_address, 3)
    i2c_bus.i2c_rdwr(read)
    reading_data = [c_uint8(x) for x in list(read)]
    raw_data_val = c_int16(reading_data[0].value << 8 | reading_data[1].value)
    crc_byte = reading_data[2]
    crc_result = None
    if crc_check:
        crc_result = check_CRC(c_uint16(raw_data_val.value), crc_byte)
    return (raw_data_val, crc_byte, crc_result)

def scale_flow_read(raw_flow_reading, scale_factor):
    '''
    A simple function to scale the output value recieved from the SF04 sensor.
    ----------------------------------------------------------------------------
    input: raw_flow_reading, scale_factor - type: c_int16, c_uint16
    output: scaled_flow_reading - type: float
    '''
    return raw_flow_reading.value/scale_factor.value

def read_scale_and_unit(i2c_bus, crc_check=False):
    '''
    Reads the user register of the SF04 Sensirion sensor and then reads
    the calibration field of the sensor each setting corresponds to an EEPROM
    address that must then be read to get the scale factor adjustment and the
    flow rate units code.
    ----------------------------------------------------------------------------
    input: i2c_bus, crc_check - type: SMBus2 bus, bool[=False]
    output: scale_factor, units_string, scale_crc_result, unit_crc_result
           - type: c_uint16, string, bool, bool
    '''
    units_dict = {2115: 'nl/min',
                  2116: 'ul/min',
                  2117: 'ml/min',
                  2100: 'ul/sec',
                  2133: 'ml/hr'}
    scale_factor_addresses = (0x2B6, 0x5B6, 0x8B6, 0xBB6, 0xEB6)
    user_reg, crc_byte, user_crc_result = read_user_reg(i2c_bus, crc_check)
    if user_crc_result is None or user_crc_result:
        scale_factor_address = c_uint16(scale_factor_addresses[(user_reg.value & 0x70) >> 4])
        i2c_bus.write_block_data(_sensor_address,
                                 _read_eeprom,
                                 [scale_factor_address.value >> 4,
                                  c_uint16(scale_factor_address.value << 12).value >> 8])
        read = i2c_msg.read(_sensor_address, 6)
        i2c_bus.i2c_rdwr(read)
        scale_and_unit = [c_uint8(x) for x in list(read)]
        scale_factor = c_uint16(scale_and_unit[0].value << 8 | scale_and_unit[1].value)
        scale_crc = scale_and_unit[2]
        unit_code = c_uint16(scale_and_unit[3].value << 8 | scale_and_unit[4].value)
        unit_crc = scale_and_unit[5]
        scale_crc_result = None
        unit_crc_result = None
        if crc_check:
            scale_crc_result = check_CRC(scale_factor, scale_crc)
            unit_crc_result = check_CRC(unit_code, unit_crc)
        return (scale_factor, units_dict[unit_code.value], scale_crc_result, unit_crc_result)
    else:
        print('CRC check failed on retrieving the user register, error codes have been transmitted')
        return (0, "Error", False, False)

def read_product_info(i2c_bus, crc_check=False):
    #TODO update function description
    '''
    Reads the user register of the SF04 Sensirion sensor and then reads
    the calibration field of the sensor each setting corresponds to an EEPROM
    address that must then be read to get the scale factor adjustment and the
    flow rate units code.
    ----------------------------------------------------------------------------
    input: i2c_bus, crc_check - type: SMBus2 bus, bool[=False]
    output: product_name, product_serial, name_crc_result, serial_crc_result
           - type: bytestring, bytestring, bool, bool
    '''
    part_name_address = c_uint16(0x2E8)
    serial_number_address = c_uint16(0x2F8)
    i2c_bus.write_block_data(_sensor_address,
                             _read_eeprom,
                             [part_name_address.value >> 4,
                              c_uint16(part_name_address.value << 12).value >> 8])
    # part name is 20 bytes with a crc byte every 2 bytes
    read = i2c_msg.read(_sensor_address, 30)
    i2c_bus.i2c_rdwr(read)
    part_name_bytes = [c_uint8(x) for x in list(read)]
    write_list = [_read_eeprom,
                  serial_number_address.value >> 4,
                  c_uint16(serial_number_address << 12).value >> 8]
    print(hex(write_list[1]), hex(write_list[1]), hex(write_list[2]))
    write = i2c_msg.write(_sensor_address, [_read_eeprom,
                                            serial_number_address.value >> 4,
                                            c_uint16(serial_number_address << 12).value >> 8])
    i2c_bus.i2c_rdwr(write)
    # i2c_bus.write_block_data(_sensor_address,
                             # _read_eeprom,
                             # [serial_number_address.value >> 4,
                              # c_uint16(serial_number_address << 12).value >> 8])
    # part serial is 4 bytes with a crc byte every 2 bytes
    read = i2c_msg.read(_sensor_address, 6)
    i2c_bus.i2c_rdwr(read)
    serial_number_bytes = [c_uint8(x) for x in list(read)]
    name_fragments = []
    for x in range(0,30,3):
        name_fragments.append((c_uint16(part_name_bytes[x].value << 8 | part_name_bytes[x+1].value), part_name_bytes[x+2]))
    serial_fragments = []
    for x in range(0,6,3):
        serial_fragments.append((c_uint16(serial_number_bytes[x].value << 8 | serial_number_bytes[x+1].value), serial_number_bytes[x+2]))
    name_crc_result = None
    serial_crc_result = None
    if crc_check:
        name_crc_result = True
        serial_crc_result = True
        for name_fragment in name_fragments:
            name_crc_result = name_crc_result and check_CRC(name_fragment[0], name_fragment[1])
        for serial_fragment in serial_fragments:
            serial_crc_result = serial_crc_result and check_CRC(serial_fragment[0], serial_fragment[1])
    product_name = b''
    for name_fragment in name_fragments:
        product_name = b''.join([product_name, name_fragment[0].to_bytes(2, 'big')])
    product_serial = b''
    for serial_fragment in serial_fragments:
        product_serial = b''.join([product_serial, serial_fragment[0].to_bytes(2, 'big')])
    return (product_name, product_serial, name_crc_result, serial_crc_result)

def check_CRC(message, crc_byte):
    '''
    Checks the reading runs it through a CRC8 checksum function to ensure data
    integrity.
    ---------------------------------------------------------------------------
    input: message, crc_byte - type: c_uint16, c_uint8
    output: checksum_result - type: bool
    '''
    crc_hash = crc8.crc8()
    crc_hash.update(message.value.to_bytes(2,'big'))
    return crc_hash.digest() == crc_byte.value.to_bytes(1, 'big')

def reset_sensor(i2c_bus):
    '''
    Perform a soft reset of the sensor.
    ---------------------------------------------------------------------------
    input: i2c_bus - type: SMBus2 bus
    output: None
    '''
    i2c_bus.write_byte(_sensor_address, _soft_rest)


