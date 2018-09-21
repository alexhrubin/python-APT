import serial
from serial.tools.list_ports import comports
import struct
import time


PRM1Z8_enc_per_degree = 1919.64 #encoder count per degree
PRM1Z8_scale_velocity = 42941.66 #degree per second
PRM1Z8_scale_acceleration = 14.66 #degree per sec^2

#motor = serial.Serial(port, baudrate=115200, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=timeout, rtscts=True)

# MGMSG_HW_REQ_INFO = b'\x05\x00\x00\x00\x50\x01'
# motor.write(MGMSG_HW_REQ_INFO)

# serial = struct.unpack("<L", response[6:10])[0]
# model_no = response[10:18]


def identify_hardware():
    open_ports = [p[0] for p in comports()]

    for port in open_ports:
        print(port)
        with serial.Serial(port) as conn:
            #if conn.is_open:
            #    print("Port ", port, " is already open! Skipping.")
                
            conn.apply_settings(port_settings)
            #conn.open()
            
            cmd = Commands['MGMSG_HW_REQ_INFO'] + b'\x00\x00' + DEVICE_ADDR + PC_ADDR
        
            conn.write(cmd)
            time.sleep(2)
            response = conn.read_all()
            print(response)



            
class MotionControl:
    def __init__(self, port):
        self.port = port
        self.port_settings = {'parity': 'N',
                 'xonxoff': False,
                 'rtscts': True,
                 'dsrdtr': False,
                 'baudrate': 115200,
                 'bytesize': 8,
                 'timeout': 0.1,
                 'stopbits': 1,
                 'write_timeout': None,
                 'inter_byte_timeout': None}
        
        DEVICE_ADDR = b'\x50'   #generic USB
        PC_ADDR = b'\01'

        self.connection = self.connect()

    def connect(self):
        c = serial.Serial(self.port)
        c.apply_settings(self.port_settings)
        return c

    def jog(self, direction):
        if direction == 'fwd':
            self.connection.write(b'j\x04\x00\x01\x50\x01')
        elif direction == 'rev':
            self.connection.write(b'j\x04\x00\x02\x50\x01')
        response = self.connection.read_all()
        print(response)
        
  #  def send_command(self, message_name):
 #       msg_id = Commands[message_name]
#        message = Message(
    
class ReqMessage:
    def __init__(self, msg_ID, msg_params, source_addr, dest_addr, description, packet_length):
        self.msg_ID = msg_ID
        self.msg_params = msg_params
        self.source_addr = source_addr
        self.dest_addr = dest_addr
        self.description = description
        self.packet_length


class Field:
    def __init__(self, value, name, first_bit, last_bit, fmt):
        self.value = value
        self.name = name
        self.first_bit = first_bit
        self.last_bit = last_bit
        self.fmt = fmt

    def encode(self):
        pass
    def decode(self):
        if fmt == 'word': #unsigned 16bit little-endian
            decoded = struct.unpack('<h', self.value)
        elif fmt == 'short': #signed 16bit little-endian
            decoded = struct.unpack('<H', self.value)
        elif fmt == 'dword': #unsigned 32bit little-endian
            decoded = struct.unpack('<I', self.value)
        elif fmt == 'long': #signed 32bit little-endian
            decoded = struct.unpack('<l', self.value)
        elif fmt == 'char':
            decoded = struct.unpack('c', self.value)
        elif fmt == 'charN':
            pass
        elif fmt == 'x':
            decoded = 'nothing'

        return decoded
            
    
class Header:
    def __init__(self, header_type, msg_name, middle_bytes, dest_addr, source_addr):
        id_bits = Commands[msg_name]
        self.id_field = Field(id_bits, "Message ID", 0, 1)

        if header_type == 1:
            self.param1 = Field(middle_bytes[0], "Parameter 1", 2, 2)
            self.param2 = Field(middle_bytes[1], "Parameter 2", 3, 3)
            self.destination_byte = Field(dest_addr, "Destination", 4, 4)
        elif header_type == 2:
            self.packet_length = Field(middle_bytes[0], "Following Packet Length", 2, 3)
            dest_addr = hex(0x80 | dest_addr)
            self.destination_byte = Field(dest_addr, "Destination", 4, 4)
        
        self.source_bit = Field(source_addr, "Source", 5, 5)

        self.bits = id_bits + param1 + param2 + dest_addr + source_addr



class Message(Header):
    def __init__(self, header_type, msg_name, param1, param2, dest_byte, source_byte, data_fields):
        param1_byte = self.encode()
        Header.__init__(header_type, msg_name, param1_byte, param2_byte, dest_byte, source_byte)

        self.data_fields = data_fields

    def encode():
        pass
    def decode():
        pass


    
    

Commands = {'MGMSG_MOD_IDENTIFY': b'#\x02',
 'MGMSG_MOD_SET_CHANENABLESTATE': b'\x10\x02',
 'MGMSG_MOD_REQ_CHANENABLESTATE': b'\x11\x02',
 'MGMSG_MOD_GET_CHANENABLESTATE': b'\x12\x02',
 'MGMSG_HW_DISCONNECT': b'\x02\x00',
 'MGMSG_HW_RESPONSE': b'\x80\x00',
 'MGMSG_HW_RICHRESPONSE': b'\x81\x00',
 'MGMSG_HW_START_UPDATEMSGS': b'\x11\x00',
 'MGMSG_HW_STOP_UPDATEMSGS': b'\x12\x00',
 'MGMSG_HW_REQ_INFO': b'\x05\x00',
 'MGMSG_HW_GET_INFO': b'\x06\x00',
 'MGMSG_RACK_REQ_BAYUSED': b'`\x00',
 'MGMSG_RACK_GET_BAYUSED': b'a\x00',
 'MGMSG_HUB_REQ_BAYUSED': b'e\x00',
 'MGMSG_HUB_GET_BAYUSED': b'f\x00',
 'MGMSG_RACK_REQ_STATUSBITS': b'&\x02',
 'MGMSG_RACK_GET_STATUSBITS': b"'\x02",
 'MGMSG_RACK_SET_DIGOUTPUTS': b'(\x02',
 'MGMSG_RACK_REQ_DIGOUTPUTS': b')\x02',
 'MGMSG_RACK_GET_DIGOUTPUTS': b'0\x02',
 'MGMSG_MOD_SET_DIGOUTPUTS': b'\x13\x02',
 'MGMSG_MOD_REQ_DIGOUTPUTS': b'\x14\x02',
 'MGMSG_MOD_GET_DIGOUTPUTS': b'\x15\x02',
 'MGMSG_HW_YES_FLASH_PROGRAMMING': b'\x17\x00',
 'MGMSG_HW_NO_FLASH_PROGRAMMING': b'\x18\x00',
 'MGMSG_MOT_SET_POSCOUNTER': b'\x10\x04',
 'MGMSG_MOT_REQ_POSCOUNTER': b'\x11\x04',
 'MGMSG_MOT_GET_POSCOUNTER': b'\x12\x04',
 'MGMSG_MOT_SET_ENCCOUNTER': b'\t\x04',
 'MGMSG_MOT_REQ_ENCCOUNTER': b'\n\x04',
 'MGMSG_MOT_GET_ENCCOUNTER': b'\x0b\x04',
 'MGMSG_MOT_SET_VELPARAMS': b'\x13\x04',
 'MGMSG_MOT_REQ_VELPARAMS': b'\x14\x04',
 'MGMSG_MOT_GET_VELPARAMS': b'\x15\x04',
 'MGMSG_MOT_SET_JOGPARAMS': b'\x16\x04',
 'MGMSG_MOT_REQ_JOGPARAMS': b'\x17\x04',
 'MGMSG_MOT_GET_JOGPARAMS': b'\x18\x04',
 'MGMSG_MOT_REQ_ADCINPUTS': b'+\x04',
 'MGMSG_MOT_GET_ADCINPUTS': b',\x04',
 'MGMSG_MOT_SET_POWERPARAMS': b'&\x04',
 'MGMSG_MOT_REQ_POWERPARAMS': b"'\x04",
 'MGMSG_MOT_GET_POWERPARAMS': b'(\x04',
 'MGMSG_MOT_SET_GENMOVEPARAMS': b':\x04',
 'MGMSG_MOT_REQ_GENMOVEPARAMS': b';\x04',
 'MGMSG_MOT_GET_GENMOVEPARAMS': b'<\x04',
 'MGMSG_MOT_SET_MOVERELPARAMS': b'E\x04',
 'MGMSG_MOT_REQ_MOVERELPARAMS': b'F\x04',
 'MGMSG_MOT_GET_MOVERELPARAMS': b'G\x04',
 'MGMSG_MOT_SET_MOVEABSPARAMS': b'P\x04',
 'MGMSG_MOT_REQ_MOVEABSPARAMS': b'Q\x04',
 'MGMSG_MOT_GET_MOVEABSPARAMS': b'R\x04',
 'MGMSG_MOT_SET_HOMEPARAMS': b'@\x04',
 'MGMSG_MOT_REQ_HOMEPARAMS': b'A\x04',
 'MGMSG_MOT_GET_HOMEPARAMS': b'B\x04',
 'MGMSG_MOT_SET_LIMSWITCHPARAMS': b'#\x04',
 'MGMSG_MOT_REQ_LIMSWITCHPARAMS': b'$\x04',
 'MGMSG_MOT_GET_LIMSWITCHPARAMS': b'%\x04',
 'MGMSG_MOT_MOVE_HOME': b'C\x04',
 'MGMSG_MOT_MOVE_HOMED': b'D\x04',
 'MGMSG_MOT_MOVE_RELATIVE': b'H\x04',
 'MGMSG_MOT_MOVE_COMPLETED': b'd\x04',
 'MGMSG_MOT_MOVE_ABSOLUTE': [b'S\x04', 1],
 'MGMSG_MOT_MOVE_JOG': [b'j\x04', 1],
 'MGMSG_MOT_MOVE_VELOCITY': [b'W\x04', 1],
 'MGMSG_MOT_MOVE_STOP': [b'e\x04', 1],
 'MGMSG_MOT_MOVE_STOPPED': b'f\x04',
 'MGMSG_MOT_SET_BOWINDEX': b'\xf4\x04',
 'MGMSG_MOT_REQ_BOWINDEX': b'\xf5\x04',
 'MGMSG_MOT_GET_BOWINDEX': b'\xf6\x04',
 'MGMSG_MOT_SET_DCPIDPARAMS': b'\xa0\x04',
 'MGMSG_MOT_REQ_DCPIDPARAMS': b'\xa1\x04',
 'MGMSG_MOT_GET_DCPIDPARAMS': b'\xa2\x04',
 'MGMSG_MOT_SET_AVMODES': b'\xb3\x04',
 'MGMSG_MOT_REQ_AVMODES': b'\xb4\x04',
 'MGMSG_MOT_GET_AVMODES': b'\xb5\x04',
 'MGMSG_MOT_SET_POTPARAMS': b'\xb0\x04',
 'MGMSG_MOT_REQ_POTPARAMS': b'\xb1\x04',
 'MGMSG_MOT_GET_POTPARAMS': b'\xb2\x04',
 'MGMSG_MOT_SET_BUTTONPARAMS': b'\xb6\x04',
 'MGMSG_MOT_REQ_BUTTONPARAMS': b'\xb7\x04',
 'MGMSG_MOT_GET_BUTTONPARAMS': b'\xb8\x04',
 'MGMSG_MOT_SET_EEPROMPARAMS': b'\xb9\x04',
 'MGMSG_MOT_SET_PMDPOSITIONLOOPPARAMS': b'\xd7\x04',
 'MGMSG_MOT_REQ_PMDPOSITIONLOOPPARAMS': b'\xd8\x04',
 'MGMSG_MOT_GET_PMDPOSITIONLOOPPARAMS': b'\xd9\x04',
 'MGMSG_MOT_SET_PMDMOTOROUTPUTPARAMS': b'\xda\x04',
 'MGMSG_MOT_REQ_PMDMOTOROUTPUTPARAMS': b'\xdb\x04',
 'MGMSG_MOT_GET_PMDMOTOROUTPUTPARAMS': b'\xdc\x04',
 'MGMSG_MOT_SET_PMDTRACKSETTLEPARAMS': b'\xe0\x04',
 'MGMSG_MOT_REQ_PMDTRACKSETTLEPARAMS': b'\xe1\x04',
 'MGMSG_MOT_GET_PMDTRACKSETTLEPARAMS': b'\xe2\x04',
 'MGMSG_MOT_SET_PMDPROFILEMODEPARAMS': b'\xe3\x04',
 'MGMSG_MOT_REQ_PMDPROFILEMODEPARAMS': b'\xe4\x04',
 'MGMSG_MOT_GET_PMDPROFILEMODEPARAMS': b'\xe5\x04',
 'MGMSG_MOT_SET_PMDJOYSTICKPARAMS': b'\xe6\x04',
 'MGMSG_MOT_REQ_PMDJOYSTICKPARAMS': b'\xe7\x04',
 'MGMSG_MOT_GET_PMDJOYSTICKPARAMS': b'\xe8\x04',
 'MGMSG_MOT_SET_PMDCURRENTLOOPPARAMS': b'\xd4\x04',
 'MGMSG_MOT_REQ_PMDCURRENTLOOPPARAMS': b'\xd5\x04',
 'MGMSG_MOT_GET_PMDCURRENTLOOPPARAMS': b'\xd6\x04',
 'MGMSG_MOT_SET_PMDSETTLEDCURRENTLOOPPARAMS': b'\xe9\x04',
 'MGMSG_MOT_REQ_PMDSETTLEDCURRENTLOOPPARAMS': b'\xea\x04',
 'MGMSG_MOT_GET_PMDSETTLEDCURRENTLOOPPARAMS': b'\xeb\x04',
 'MGMSG_MOT_SET_PMDSTAGEAXISPARAMS': b'\xf0\x04',
 'MGMSG_MOT_REQ_PMDSTAGEAXISPARAMS': b'\xf1\x04',
 'MGMSG_MOT_GET_PMDSTAGEAXISPARAMS': b'\xf2\x04',
 'MGMSG_MOT_SET_TSTACTUATORTYPE': b'\xfe\x04',
 'MGMSG_MOT_GET_STATUSUPDATE': b'\x81\x04',
 'MGMSG_MOT_REQ_STATUSUPDATE': b'\x80\x04',
 'MGMSG_MOT_GET_DCSTATUSUPDATE': b'\x91\x04',
 'MGMSG_MOT_REQ_DCSTATUSUPDATE': b'\x90\x04',
 'MGMSG_MOT_ACK_DCSTATUSUPDATE': b'\x92\x04',
 'MGMSG_MOT_REQ_STATUSBITS': b')\x04',
 'MGMSG_MOT_GET_STATUSBITS': b'*\x04',
 'MGMSG_MOT_SUSPEND_ENDOFMOVEMSGS': b'k\x04',
 'MGMSG_MOT_RESUME_ENDOFMOVEMSGS': b'l\x04',
 'MGMSG_MOT_SET_TRIGGER': b'\x00\x05',
 'MGMSG_MOT_REQ_TRIGGER': b'\x01\x05',
 'MGMSG_MOT_GET_TRIGGER': b'\x02\x05',
 'MGMSG_MOT_SET_KCUBEMMIPARAMS': b' \x05',
 'MGMSG_MOT_REQ_KCUBEMMIPARAMS': b'!\x05',
 'MGMSG_MOT_GET_KCUBEMMIPARAMS': b'"\x05',
 'MGMSG_MOT_SET_KCUBETRIGIOCONFIG': b'#\x05',
 'MGMSG_MOT_REQ_KCUBETRIGCONFIG': b'$\x05',
 'MGMSG_MOT_GET_KCUBETRIGCONFIG': b'%\x05',
 'MGMSG_MOT_SET_KCUBEPOSTRIGPARAMS': b'&\x05',
 'MGMSG_MOT_REQ_KCUBEPOSTRIGPARAMS': b"'\x05",
 'MGMSG_MOT_GET_KCUBEPOSTRIGPARAMS': b'(\x05',
 'MGMSG_MOT_SET_MFF_OPERPARAMS': b'\x10\x05',
 'MGMSG_MOT_REQ_MFF_OPERPARAMS': b'\x11\x05',
 'MGMSG_MOT_GET_MFF_OPERPARAMS': b'\x12\x05',
 'MGMSG_MOT_SET_SOL_OPERATINGMODE': b'\xc0\x04',
 'MGMSG_MOT_REQ_SOL_OPERATINGMODE': b'\xc1\x04',
 'MGMSG_MOT_GET_SOL_OPERATINGMODE': b'\xc2\x04',
 'MGMSG_MOT_SET_SOL_CYCLEPARAMS': b'\xc3\x04',
 'MGMSG_MOT_REQ_SOL_CYCLEPARAMS': b'\xc4\x04',
 'MGMSG_MOT_GET_SOL_CYCLEPARAMS': b'\xc5\x04',
 'MGMSG_MOT_SET_SOL_INTERLOCKMODE': b'\xc6\x04',
 'MGMSG_MOT_REQ_SOL_INTERLOCKMODE': b'\xc7\x04',
 'MGMSG_MOT_GET_SOL_INTERLOCKMODE': b'\xc8\x04',
 'MGMSG_MOT_SET_SOL_STATE': b'\xcb\x04',
 'MGMSG_MOT_REQ_SOL_STATE': b'\xcc\x04',
 'MGMSG_MOT_GET_SOL_STATE': b'\xcd\x04',
 'MGMSG_PZ_SET_POSCONTROLMODE': b'@\x06',
 'MGMSG_PZ_REQ_POSCONTROLMODE': b'A\x06',
 'MGMSG_PZ_GET_POSCONTROLMODE': b'B\x06',
 'MGMSG_PZ_SET_OUTPUTVOLTS': b'C\x06',
 'MGMSG_PZ_REQ_OUTPUTVOLTS': b'D\x06',
 'MGMSG_PZ_GET_OUTPUTVOLTS': b'E\x06',
 'MGMSG_PZ_SET_OUTPUTPOS': b'F\x06',
 'MGMSG_PZ_REQ_OUTPUTPOS': b'G\x06',
 'MGMSG_PZ_GET_OUTPUTPOS': b'H\x06',
 'MGMSG_PZ_SET_INPUTVOLTSSRC': b'R\x06',
 'MGMSG_PZ_REQ_INPUTVOLTSSRC': b'S\x06',
 'MGMSG_PZ_GET_INPUTVOLTSSRC': b'T\x06',
 'MGMSG_PZ_SET_PICONSTS': b'U\x06',
 'MGMSG_PZ_REQ_PICONSTS': b'V\x06',
 'MGMSG_PZ_GET_PICONSTS': b'W\x06',
 'MGMSG_PZ_REQ_PZSTATUSBITS': b'[\x06',
 'MGMSG_PZ_GET_PZSTATUSBITS': b'\\\x06',
 'MGMSG_PZ_GET_PZSTATUSUPDATE': b'a\x06',
 'MGMSG_PZ_ACK_PZSTATUSUPDATE': b'b\x06',
 'MGMSG_PZ_SET_OUTPUTLUT': b'\x00\x07',
 'MGMSG_PZ_REQ_OUTPUTLUT': b'\x01\x07',
 'MGMSG_PZ_GET_OUTPUTLUT': b'\x02\x07',
 'MGMSG_PZ_SET_OUTPUTLUTPARAMS': b'\x03\x07',
 'MGMSG_PZ_REQ_OUTPUTLUTPARAMS': b'\x04\x07',
 'MGMSG_PZ_GET_OUTPUTLUTPARAMS': b'\x05\x07',
 'MGMSG_PZ_START_LUTOUTPUT': b'\x06\x07',
 'MGMSG_PZ_STOP_LUTOUTPUT': b'\x07\x07',
 'MGMSG_PZ_SET_EEPROMPARAMS': b'\xd0\x07',
 'MGMSG_PZ_SET_TPZ_DISPSETTINGS': b'\xd1\x07',
 'MGMSG_PZ_REQ_TPZ_DISPSETTINGS': b'\xd2\x07',
 'MGMSG_PZ_GET_TPZ_DISPSETTINGS': b'\xd3\x07',
 'MGMSG_PZ_SET_TPZ_IOSETTINGS': b'\xd4\x07',
 'MGMSG_PZ_REQ_TPZ_IOSETTINGS': b'\xd5\x07',
 'MGMSG_PZ_GET_TPZ_IOSETTINGS': b'\xd6\x07',
 'MGMSG_PZ_SET_ZERO': b'X\x06',
 'MGMSG_PZ_REQ_MAXTRAVEL': b'P\x06',
 'MGMSG_PZ_GET_MAXTRAVEL': b'Q\x06',
 'MGMSG_PZ_SET_IOSETTINGS': b'p\x06',
 'MGMSG_PZ_REQ_IOSETTINGS': b'q\x06',
 'MGMSG_PZ_GET_IOSETTINGS': b'r\x06',
 'MGMSG_PZ_SET_OUTPUTMAXVOLTS': b'\x80\x06',
 'MGMSG_PZ_REQ_OUTPUTMAXVOLTS': b'\x81\x06',
 'MGMSG_PZ_GET_OUTPUTMAXVOLTS': b'\x82\x06',
 'MGMSG_PZ_SET_TPZ_SLEWRATES': b'\x83\x06',
 'MGMSG_PZ_REQ_TPZ_SLEWRATES': b'\x84\x06',
 'MGMSG_PZ_GET_TPZ_SLEWRATES': b'\x85\x06',
 'MGMSG_MOT_SET_PZSTAGEPARAMDEFAULTS': b'\x86\x06',
 'MGMSG_PZ_SET_LUTVALUETYPE:': b'\x08\x07',
 'MGMSG_KPZ_SET_KCUBEMMIPARAMS': b'\xf0\x07',
 'MGMSG_KPZ_REQ_KCUBEMMIPARAMS': b'\xf1\x07',
 'MGMSG_KPZ_GET_KCUBEMMIPARAMS': b'\xf2\x07',
 'MGMSG_KPZ_SET_KCUBETRIGIOCONFIG': b'\xf3\x07',
 'MGMSG_KPZ_REQ_KCUBETRIGIOCONFIG': b'\xf4\x07',
 'MGMSG_KPZ_GET_KCUBETRIGIOCONFIG': b'\xf5\x07',
 'MGMSG_PZ_SET_TSG_IOSETTINGS': b'\xda\x07',
 'MGMSG_PZ_REQ_TSG_IOSETTINGS': b'\xdb\x07',
 'MGMSG_PZ_GET_TSG_IOSETTINGS': b'\xdc\x07',
 'MGMSG_PZ_REQ_TSG_READING': b'\xdd\x07',
 'MGMSG_PZ_GET_TSG_READING': b'\xde\x07',
 'MGMSG_KSG_SET_KCUBEMMIPARAMS': b'\xf6\x07',
 'MGMSG_KSG_REQ_KCUBEMMIPARAMS': b'\xf7\x07',
 'MGMSG_KSG_GET_KCUBEMMIPARAMS': b'\xf8\x07',
 'MGMSG_KSG_SET_KCUBETRIGIOCONFIG': b'\xf9\x07',
 'MGMSG_KSG_REQ_KCUBETRIGIOCONFIG': b'\xfa\x07',
 'MGMSG_KSG_GET_KCUBETRIGIOCONFIG': b'\xfb\x07',
 'MGMSG_PZ_SET_NTMODE': b'\x03\x06',
 'MGMSG_PZ_REQ_NTMODE': b'\x04\x06',
 'MGMSG_PZ_GET_NTMODE': b'\x05\x06',
 'MGMSG_PZ_SET_NTTRACKTHRESHOLD': b'\x06\x06',
 'MGMSG_PZ_REQ_NTTRACKTHRESHOLD': b'\x07\x06',
 'MGMSG_PZ_GET_NTTRACKTHRESHOLD': b'\x08\x06',
 'MGMSG_PZ_SET_NTCIRCHOMEPOS': b'\t\x06',
 'MGMSG_PZ_REQ_NTCIRCHOMEPOS': b'\x10\x06',
 'MGMSG_PZ_GET_NTCIRCHOMEPOS': b'\x11\x06',
 'MGMSG_PZ_MOVE_NTCIRCTOHOMEPOS': b'\x12\x06',
 'MGMSG_PZ_REQ_NTCIRCCENTREPOS': b'\x13\x06',
 'MGMSG_PZ_GET_NTCIRCCENTREPOS': b'\x14\x06',
 'MGMSG_PZ_SET_NTCIRCPARAMS': b'\x18\x06',
 'MGMSG_PZ_REQ_NTCIRCPARAMS': b'\x19\x06',
 'MGMSG_PZ_GET_NTCIRCPARAMS': b' \x06',
 'MGMSG_PZ_SET_NTCIRCDIA': b'\x1a\x06',
 'MGMSG_PZ_SET_NTCIRCDIALUT': b'!\x06',
 'MGMSG_PZ_REQ_NTCIRCDIALUT': b'"\x06',
 'MGMSG_PZ_GET_NTCIRCDIALUT': b'#\x06',
 'MGMSG_PZ_SET_NTPHASECOMPPARAMS': b'&\x06',
 'MGMSG_PZ_REQ_NTPHASECOMPPARAMS': b"'\x06",
 'MGMSG_PZ_GET_NTPHASECOMPPARAMS': b'(\x06',
 'MGMSG_PZ_SET_NTTIARANGEPARAMS': b'0\x06',
 'MGMSG_PZ_REQ_NTTIARANGEPARAMS': b'1\x06',
 'MGMSG_PZ_GET_NTTIARANGEPARAMS': b'2\x06',
 'MGMSG_PZ_SET_NTGAINPARAMS': b'3\x06',
 'MGMSG_PZ_REQ_NTGAINPARAMS': b'4\x06',
 'MGMSG_PZ_GET_NTGAINPARAMS': b'5\x06',
 'MGMSG_PZ_SET_NTTIALPFILTERPARAMS': b'6\x06',
 'MGMSG_PZ_REQ_NTTIALPFILTERPARAMS': b'7\x06',
 'MGMSG_PZ_GET_NTTIALPFILTERPARAMS': b'8\x06',
 'MGMSG_PZ_REQ_NTTIAREADING': b'9\x06',
 'MGMSG_PZ_GET_NTTIAREADING': b':\x06',
 'MGMSG_PZ_SET_NTFEEDBACKSRC': b';\x06',
 'MGMSG_PZ_REQ_NTFEEDBACKSRC': b'<\x06',
 'MGMSG_PZ_GET_NTFEEDBACKSRC': b'=\x06',
 'MGMSG_PZ_REQ_NTSTATUSBITS': b'>\x06',
 'MGMSG_PZ_GET_NTSTATUSBITS': b'?\x06',
 'MGMSG_PZ_REQ_NTSTATUSUPDATE': b'd\x06',
 'MGMSG_PZ_GET_NTSTATUSUPDATE': b'e\x06',
 'MGMSG_PZ_ACK_NTSTATUSUPDATE': b'f\x06',
 'MGMSG_NT_SET_EEPROMPARAMS': b'\xe7\x07',
 'MGMSG_NT_SET_TNA_DISPSETTINGS': b'\xe8\x07',
 'MGMSG_NT_REQ_TNA_DISPSETTINGS': b'\xe9\x07',
 'MGMSG_NT_GET_TNA_DISPSETTINGS': b'\xea\x07',
 'MGMSG_NT_SET_TNAIOSETTINGS': b'\xeb\x07',
 'MGMSG_NT_REQ_TNAIOSETTINGS': b'\xec\x07',
 'MGMSG_NT_GET_TNAIOSETTINGS': b'\xed\x07',
 'MGMSG_LA_SET_PARAMS': b'\x00\x08',
 'MGMSG_LA_REQ_PARAMS': b'\x01\x08',
 'MGMSG_LA_GET_PARAMS': b'\x02\x08',
 'MGMSG_LA_SET_EEPROMPARAMS': b'\x10\x08',
 'MGMSG_LA_ENABLEOUTPUT': b'\x11\x08',
 'MGMSG_LA_DISABLEOUTPUT': b'\x12\x08',
 'MGMSG_LD_OPENLOOP': b'\x13\x08',
 'MGMSG_LD_CLOSEDLOOP': b'\x14\x08',
 'MGMSG_LD_POTROTATING': b'\x15\x08',
 'MGMSG_LD_MAXCURRENTADJUST': b'\x16\x08',
 'MGMSG_LD_SET_MAXCURRENTDIGPOT': b'\x17\x08',
 'MGMSG_LD_REQ_MAXCURRENTDIGPOT': b'\x18\x08',
 'MGMSG_LD_GET_MAXCURRENTDIGPOT': b'\x19\x08',
 'MGMSG_LD_FINDTIAGAIN': b'\x1a\x08',
 'MGMSG_LD_TIAGAINADJUST': b'\x1b\x08',
 'MGMSG_LA_REQ_STATUSUPDATE': b' \x08',
 'MGMSG_LA_GET_STATUSUPDATE': b'!\x08',
 'MGMSG_LA_ACK_STATUSUPDATE': b'"\x08',
 'MGMSG_LD_REQ_STATUSUPDATE': b'%\x08',
 'MGMSG_LD_GET_STATUSUPDATE': b'&\x08',
 'MGMSG_LD_ACK_STATUSUPDATE': b"'\x08",
 'MGMSG_QUAD_SET_PARAMS': b'p\x08',
 'MGMSG_QUAD_REQ_PARAMS': b'q\x08',
 'MGMSG_QUAD_GET_PARAMS': b'r\x08',
 'MGMSG_QUAD_REQ_STATUSUPDATE': b'\x80\x08',
 'MGMSG_QUAD_GET_STATUSUPDATE': b'\x81\x08',
 'MGMSG_QUAD_ACK_STATUSUPDATE': b'\x82\x08',
 'MGMSG_QUAD_SET_EEPROMPARAMS': b'u\x08',
 'MGMSG_TEC_SET_PARAMS': b'@\x08',
 'MGMSG_TEC_REQ_PARAMS': b'A\x08',
 'MGMSG_TEC_GET_PARAMS': b'B\x08',
 'MGMSG_TEC_SET_EEPROMPARAMS': b'P\x08',
 'MGMSG_TEC_REQ_STATUSUPDATE': b'`\x08',
 'MGMSG_TEC_GET_STATUSUPDATE': b'a\x08',
 'MGMSG_TEC_ACK_STATUSUPDATE': b'b\x08',
 'MGMSG_PZMOT_SET_PARAMS': b'\xc0\x08',
 'MGMSG_PZMOT_REQ_PARAMS': b'\xc1\x08',
 'MGMSG_PZMOT_GET_PARAMS': b'\xc2\x08',
 'MGMSG_PZMOT_MOVE_ABSOLUTE': b'\xd8\x04',
 'MGMSG_PZMOT_MOVE_COMPLETED': b'\xd6\x08',
 'MGMSG_PZMOT_MOVE_JOG': b'\xd9\x08',
 'MGMSG_PZMOT_GET_STATUSUPDATE': b'\xe1\x08'}    
