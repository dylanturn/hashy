from __future__ import absolute_import, print_function
import numpy as np
import time
import file_handler
import opencl_device

class GPU_Hash():

    def __init__(self):
        self.file_path = "example_data"
        self.file_block_size = 8192

        self.file_handler = file_handler.FileHandler(self.file_path, self.file_block_size)
        self.device = opencl_device.Device(block_size=self.file_block_size)

    def main(self):

        gpu_start = time.time()

        host_hash_buffer = np.zeros(self.file_handler.set_size, dtype=np.long)
        device_hash_buffer = self.device.allocate_device_data_hash_memory(host_hash_buffer)

        print("\nProcessing {} blocks...".format(self.file_handler.file_block_count))

        for i in range(self.file_handler.file_block_count):
        #for i in range(4):
            # Hash the list of file blocks
            # print("Process Block: {}".format(i))
            self.device.hash_data_block_set(
                device_hash_set_pointer=device_hash_buffer,
                data_block_set=self.file_handler.get_next_block_set(),
                data_set_size=self.file_handler.set_size)

        print("\nProcessing Done!\n")

        self.device.copy_hash_set_from_device(device_hash_buffer, host_hash_buffer)

        gpu_end = time.time()

        self.print_results((gpu_end - gpu_start), host_hash_buffer=host_hash_buffer)

    def print_results(self, time_delta, host_hash_buffer):
        print("Target Device:       ", self.device.name())
        print("OpenCL Elapsed Time: ", (time_delta * 1000))
        print("File Block Size:     ", self.file_block_size)

        for block in host_hash_buffer:
            print("File Hash:           ", block)

if __name__ == "__main__":
    # execute only if run as a script
    GPU_Hash().main()