import struct
from functools import reduce
import serial
from serial.tools.list_ports import comports

class Controller:
    def __init__(self, port, controller_type, description):
        self.controller_type = controller_type
        self.description = description
        self.connection = serial.Serial(port,
                               baudrate=115200,
                               bytesize=serial.EIGHTBITS,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,
                               timeout=0.1,
                               rtscts=True)


class Stage:
    def __init__(self, stage_type, calibration):
        self.stage_type = stage_type
        self.position_cal = calibration['position']
        self.velocity_cal = calibration['velocity']
        self.acceleration_cal = calibration['acceleration']
        
    def Pos_APT(self, position): # position in degrees
        return position * self.position_cal
    
    def Vel_APT(self, velocity): # velocity in degre per second
        return velocity * self.velocity_cal

    def Acc_APT(self, acceleration): # acceleration in degrees per second^2
        return acceleration * self.acceleration_cal

    
        


class PRM1Z8(Stage):
    def __init__(self, port):
        calibration = {'position' : 1919.64, #count per degree
                       'velocity' : 42941.66, #degree per second
                       'acceleration' : 14.66} #degree per second squared

        Stage.__init__(self, 'PRM1-Z8', calibration)

class KDC101(Controller):
    def __init__(self, port):
        Controller.__init__(self, port)
        
        
        
    
class Field:
    def __init__(self, name, bitrange, fmt):
        self.name = name
        self.bitrange = bitrange
        self.length = self.bitrange[1] - self.bitrange[0]
        self.fmt = fmt
        
    def encode(self, value):
        if self.fmt == 'c':
            encoded = bytes(value, 'utf-8')
        elif self.fmt in ['<l', '<h']:
            encoded = value.to_bytes(self.length, 'little')
            
        padding = b'\x00' * (self.length - len(encoded))
        encoded = encoded + padding
        return encoded

    def decode(self, value):
        if self.fmt == 'c':
            decoded = value.decode('utf-8')
            decoded = decoded.strip('\x00')
        elif self.fmt == '<l' and self.length == 1:
            decoded = value[0]
        else:
            decoded = struct.unpack(self.fmt, value)[0]
        return decoded

        # '<h'  'word' #unsigned 16bit little-endian
        # '<H' 'short': #signed 16bit little-endian
        # '<I' 'dword': #unsigned 32bit little-endian
        # '<l'  'long': #signed 32bit little-endian
        # 'c' 'char':

   

class Header:
    def __init__(self, packet_follows):
        self.id_field = Field("Message ID", [0,2], '<h')

        self.source_byte = Field("Source", [5,6], '<l')
        self.destination_byte = Field("Destination", [4,5], '<l')

        if packet_follows:
            self.packet_length = Field("Packet Length", [2,4], '<hb1')
            self.fields = [self.id_field, self.packet_length, self.destination_byte, self.source_byte]
        else: 
            self.param1 = Field("Parameter 1", [2,3], '<l')
            self.param2 = Field("Parameter 2", [3,4], '<l')
            self.fields = [self.id_field, self.param1, self.param2, self.destination_byte, self.source_byte]
            
    def encode(self, values):
        encoded = []
        
        if len(values) == 4:
            values[2] = 128 | values[2]
            
        for pair in zip(self.fields, values):
            encoded.append(pair[0].encode(pair[1]))
        encoded = reduce(lambda a,b: a+b, encoded)
        return encoded
            

    def decode(self, raw_message):
        decoded = {}
        for field in self.fields:
            section = raw_message[field.bitrange[0] : field.bitrange[1]]
            decoded[field.name] = field.decode(section)
        return decoded
        
 
class OutMessage:
    def __init__(self, msg_num, p1, p2, dest, src, packet_fields):
        self.header = Header(msg_num, p1, p2, dest, src) 
        self.fields = [f for f in self.header.fields]
        
    def encode(self):
        return reduce(lambda a,b: a+b, map(lambda x: x.encode(), self.fields))

class InMessage:
    def __init__(self, raw_message, header_type, packet_fields):
        self.raw_message = raw_message

    def decode(self):
        decoded = dict()
        decoded['msg_type'] = self.raw_message
      #  if self.header_type == 1:
            

      
class MGMSG_HW_GET_INFO(Header):
    def __init__(self):
        self.head = Header(True)
        self.serial_no = Field('Serial Number', [6,10], '<l')
        self.model_no = Field('Model Number', [10,18], 'c')
        self.controller_type = Field('Controller Type', [18,20], '<h')
        self.firmware_version = Field('Firmware Version', [20,24], '<l')
        self.hw_version = Field('Hardware Version', [84,86], '<h')
        self.mod_state = Field('Modification State', [86,88], '<h')
        self.nchs = Field('Num. of Channels', [88,90], '<h')

        self.fields = self.head.fields + [self.serial_no, self.model_no, self.controller_type,
                       self.firmware_version, self.hw_version, self.mod_state, self.nchs]

    def decode(self, raw_message):
        decoded = {}
        for field in self.fields:
            print(field.name)
            section = raw_message[field.bitrange[0] : field.bitrange[1]]
            decoded[field.name] = field.decode(section)
        return decoded



def identify_hardware():
    open_ports = [p[0] for p in comports()]

    for port in open_ports:
        print(port)
        with serial.Serial(port,
                               baudrate=115200,
                               bytesize=serial.EIGHTBITS,
                               parity=serial.PARITY_NONE,
                               stopbits=serial.STOPBITS_ONE,
                               timeout=0.1,
                               rtscts=True) as conn:
            #if conn.is_open:
            #    print("Port ", port, " is already open! Skipping.")
                
 #           conn.apply_settings(port_settings)
#            #conn.open()
            
            cmd = b'\x05\x00\x00\x00P\x01'
        
            conn.write(cmd)
            time.sleep(2)
            response = conn.read_all()
            print(response)
