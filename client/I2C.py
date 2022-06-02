import smbus
import math
import signal
from contextlib import contextmanager

DEFAULT_READ_TIMEOUT = 1

class TimeoutException(Exception): pass

@contextmanager
def read_time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("I2C read timed out")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)
        
def write_bit(bus, address, reg, bit, value):
    if bit > 7 or bit < 0:
        raise IndexError('\'bit\' index is out of range')
    if value > 1 or value < 0:
        raise ValueError('\'value\' must be equal to 1 or 0')
    byte = bus.read_byte_data(address, reg)
    if value:
        byte |= (1 << bit)
    else:
        byte &= ~(1 << bit)
    bus.write_byte_data(address, reg, byte)

def write_bits(bus, address, reg, bit, length, value):
    if bit > 7 or bit < 0:
        raise IndexError('\'bit\' index is out of range')
    if length > bit + 1:
        raise IndexError('bit sequence is to long')
    if value >= 2**length:
        raise ValueError('\'value\' binary notation must be lesser then \'length\'')
    if value < 0:
        raise ValueError('\'value\' must be greater or equal to 0')
    clear_mask = (2**(bit+1)-1)^(2**(bit - length + 1)-1)
    byte = bus.read_byte_data(address, reg)
    byte = byte ^ (byte & clear_mask)
    byte |= value << (bit - length + 1)
    bus.write_byte_data(address, reg, byte)
    
def write_byte(bus, address, reg, value):
    bus.write_byte_data(address, reg, value)

def write_word(bus, address, reg, value):
    bus.write_byte_data(address, reg, value >> 8)
    bus.write_byte_data(address, reg + 1, value % 256)
    
def write_signed_word(bus, address, reg, value):
    if value < 0:
        value = -((-value - 1) - 65535)
    bus.write_byte_data(address, reg, value >> 8)
    bus.write_byte_data(address, reg + 1, value % 256)
    
def read_bit(bus, address, reg, bit, read_timeout=DEFAULT_READ_TIMEOUT):
    if bit > 7 or bit < 0:
        raise IndexError('\'bit\' index is out of range')
    with read_time_limit(read_timeout):
        byte = bus.read_byte_data(address, reg)
    result = (byte & (1 << bit)) >> bit 
    return result
    
def read_bits(bus, address, reg, bit, length, read_timeout=DEFAULT_READ_TIMEOUT):
    if bit > 7 or bit < 0:
        raise IndexError('\'bit\' index is out of range')
    if length > bit + 1:
        raise IndexError('bit sequence is to long')
    with read_time_limit(read_timeout):
        byte = bus.read_byte_data(address, reg)
    mask = 2**(bit + 1) - 1
    result = (byte & mask) >> (bit - length + 1)
    return result

def read_byte(bus, address, reg, read_timeout=DEFAULT_READ_TIMEOUT):
    with read_time_limit(read_timeout):
        result = bus.read_byte_data(address, reg)
    return result

def read_word(bus, address, reg, read_timeout=DEFAULT_READ_TIMEOUT):
    with read_time_limit(read_timeout):
        buffer = bus.read_i2c_block_data(address, reg, 2)
    result = (buffer[0] << 8) + buffer[1]
    return result

def read_signed_word(bus, address, reg, read_timeout=DEFAULT_READ_TIMEOUT):
    result = read_word(bus, address, reg, read_timeout)
    if (result >= 0x8000):
        return -((65535 - result) + 1)
    else:
        return result

def write_bytes(bus, address, reg, values):
    bus.write_i2c_block_data(address, reg, values)

def read_bytes(bus, address, reg, length, read_timeout=DEFAULT_READ_TIMEOUT):
    with read_time_limit(read_timeout):
        result = bus.read_i2c_block_data(address, reg, length)
    return result