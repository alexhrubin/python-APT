import struct

class Field:
    def __init__(self, value, bitrange, fmt):
        self.value = value
        self.bitrange = bitrange
        self.length = self.bitrange[1] - self.bitrange[0]
        self.fmt = fmt
        
    def encode(self):
        base = bytearray(b'x\00') * (self.bitrange[1] - self.bitrange[0])
        
        if type(self.value) == str:
            encoded = bytes(self.value, 'utf-8')
        elif type(self.value) == int:
            encoded = self.value.to_bytes(self.length, 'little')
            
        padding = b'\x00' * (self.length - len(encoded))
        encoded = encoded + padding
        return encoded
        
            
            
            
    def decode(self):
        decoded = struct.unpack(to_decode, self.value)
        return decoded

class Header:
    def __init__(self, msg_num, p1, p2, dest_addr, src_addr):
        msg_id = Field(msg_num, [0:2], int)
        param1 = Field(p1, [2,3], int)
        param2 = Field(p2, [3,4], int)
        dest = Field(dest_addr, [4,5], int)
        source = Field(source_addr, [5,6], int)
 
 class Message:
     def __init__(self, msg_num, p1, p2, dest, src):
         header = Header(msg_num, p1, p2, dest, src)
         
