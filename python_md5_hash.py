import hashlib
import os
import time
BLOCKSIZE = 65536
hasher = hashlib.md5()
file_path = "example_data"

print("Starting Python MD5 Baseline Test...")
files = os.listdir(file_path)

gpu_start = time.time()

for file in files:
    with open("{}/{}".format(file_path, file), 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    print(hasher.hexdigest())

gpu_end = time.time()
time_delta = (gpu_end - gpu_start)
print("Python Elapsed Time: {}ms".format(int(time_delta * 1000)))
