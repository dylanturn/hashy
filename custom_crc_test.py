import file_handler
import binascii
import time
from threading import Thread
from time import sleep


def create_table():
    a = []
    for i in range(512):
        k = i
        for j in range(8):
            if k & 1:
                k ^= 0x1db710640
            k >>= 1
        a.append(k)
    return a


def crc_update(buf, crc):
    crc ^= 0xffffffff
    for k in buf:
        crc = (crc >> 8) ^ crc_table[(crc & 0xff) ^ k]
    return crc ^ 0xffffffff

def hash(file_path):
    with open(file_path, 'rb') as f:
        print("binascii:         ", hex(binascii.crc32(f.read()) & 0xffffffff))



file_path = "test/testFile_0.junk"

# Open the file handler
in_file = file_handler.File(file_path, 8192)

# Create the CRC lookup table
crc_table = create_table()

file_crc = 0
#for i in range(in_file.get_block_count()):
#    data_block = bytearray(in_file.read_block())
##    file_crc = crc_update(data_block, file_crc)

#print("crc_update_block: ", hex(file_crc))

#with open(file_path,'rb') as f:
#    print("crc_update_rt:    ", hex(crc_update(f.read(), 0)))



start = time.time()

Thread(target = hash, args = (file_path, )).start()
Thread(target = hash, args = (file_path, )).start()
thread = Thread(target = hash, args = (file_path, ))
thread.start()
thread.join()

end = time.time()

asdf = int((end-start)*1000)

print("Run Time: {}".format(asdf))