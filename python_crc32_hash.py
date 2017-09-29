import os
import time
import binascii
from threading import Thread

def hash_file(file_path):
    with open(file_path, 'rb') as f:
        print("binascii:         ", hex(binascii.crc32(f.read()) & 0xffffffff))

file_path = "example_data"

print("Starting Python MD5 Baseline Test...")
files = os.listdir(file_path)

gpu_start = time.time()
thread_pool = []

for file in files:
    fpath = "{}/{}".format(file_path, file)
    new_thread = Thread(target=hash_file, args=(fpath,))
    new_thread.start()
    thread_pool.append(new_thread)

for thread in thread_pool:
    assert type(thread) is Thread, thread.join()


gpu_end = time.time()
time_delta = (gpu_end - gpu_start)
print("Python Elapsed Time: {}ms".format(int(time_delta * 1000)))
