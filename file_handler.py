import os
import numpy as np
import math

class FileHandler:

    def __init__(self, file_path, file_block_size):
        print("loading files...")
        files = os.listdir(file_path)
        file_set = []

        for file in files:
            new_file = File(file_path="{}/{}".format(file_path, file), block_size=file_block_size)
            file_set.append(new_file)
            self.file_block_count = new_file.block_count

        self.file_block_size = file_block_size
        self.set_size = len(file_set)
        self.file_set = file_set

    def get_next_block_set(self):
        file_block_set = np.empty(self.set_size, dtype='S{}'.format(self.file_block_size))
        for index in range(0, self.set_size):
            file_block_set[index] = self.file_set[index].read_block()

        return file_block_set


class File:

    def __init__(self, file_path, block_size=8192):

        self.file_path = file_path
        self.block_size = block_size
        self.file_size = os.path.getsize(file_path)
        self.block_count = math.ceil(os.path.getsize(file_path)/self.block_size)

        print("Opening File: ", file_path)
        print("File Size:    ", self.file_size)
        print("Block Size:   ", self.block_size)
        print("File Blocks:  ", self.block_count)
        print(" ")
        self.open_file = open(file_path, "rb")

    def read_block(self):
        file_block = self.open_file.read(self.block_size)

        if len(file_block) < self.block_size:
            return file_block.ljust(self.block_size, b"\x0f")
        else:
            return file_block

    def close_file(self):
        self.open_file.close()

    def get_file_path(self):
        return self.file_path

    def get_block_size(self):
        return self.block_size

    def get_file_size(self):
        return self.file_size

    def get_block_count(self):
        return self.block_count


# ---- Save for later ---
        # Run on the CPU
        #target_device = self.Setup_Environment(cl.device_type.CPU, 0); print("Running on CPU 0")

        # Run on the integrated GPU
        #target_device = self.Setup_Environment(cl.device_type.GPU, 0); print("Running on GPU 0")

        # Run on the discrete GPU
        #target_device = self.Setup_Environment(cl.device_type.GPU, 1); print("Running on GPU 1")

# ----------------------