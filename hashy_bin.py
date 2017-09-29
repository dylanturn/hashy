from __future__ import absolute_import, print_function
import numpy as np
import pyopencl as cl
import time
import file_handler
import opencl_device
import argparse

class OpenCL_Hash():

    def __init__(self, file_path="example_data", file_block_size=8192, device_class="CPU", device_index=0, platform_index=0):

        self.file_path = file_path

        self.file_block_size = file_block_size

        self.file_handler = file_handler.FileHandler(self.file_path, self.file_block_size)

        if device_class == "CPU":
            self.device = opencl_device.Device(block_size=self.file_block_size, device_type=cl.device_type.CPU,
                                               device_index=device_index, platform_index=platform_index)
        elif device_class == "GPU":
            self.device = opencl_device.Device(block_size=self.file_block_size, device_type=cl.device_type.GPU, device_index=device_index, platform_index=platform_index)

    def main(self, sample_percent, verbose):

        gpu_start = time.time()

        host_hash_buffer = np.zeros(self.file_handler.set_size, dtype=np.long)
        device_hash_buffer = self.device.allocate_device_hash_memory(host_hash_buffer)

        blocks_to_hash = int(int(self.file_handler.file_block_count)*sample_percent)

        if verbose:
            print("{}% of blocks is {}".format((sample_percent*100), blocks_to_hash))
            print("\nProcessing {} blocks...".format(self.file_handler.file_block_count))

        for i in range(blocks_to_hash):
            self.device.hash_data_block_set(
                device_hash_set_pointer=device_hash_buffer,
                data_block_set=self.file_handler.get_next_block_set(),
                data_set_size=self.file_handler.set_size)

        print("\nProcessing Done!\n")

        self.device.copy_hash_set_from_device(device_hash_buffer, host_hash_buffer)

        gpu_end = time.time()

        print("File Copy Time: ", int(self.file_handler.copy_time_ms*1000))
        print("Buffer Data:    ", self.device.buffer_data_ms)
        print("Release Buffer: ", self.device.release_buffer_ms)
        print("Kernel Execure: ", self.device.kernel_execute_ms)
        print(" ")

        self.print_results((gpu_end - gpu_start), host_hash_buffer, (sample_percent*100), blocks_to_hash, self.file_handler.file_block_count, verbose)

    def print_results(self, time_delta, host_hash_buffer, percent_blocks_hashed, blocks_hashed, total_blocks, verbose):
        print("----------Results----------")
        print("Target Device:       ", self.device.name())
        print("OpenCL Elapsed Time:  {}ms".format(int(time_delta * 1000)))
        print("File Block Size:     ", self.file_block_size)
        print("File Count:          ", self.file_handler.set_size)
        print("Total Blocks Hashed: ", blocks_hashed)
        print("Hash Throughput:      {} hash/ms".format(blocks_hashed/int(time_delta * 1000)))
        print("Total File Blocks:   ", int(total_blocks))
        print("Block Sample Size:    {}%".format(int(percent_blocks_hashed)))
        print("---------------------------\n")
        if verbose:
            for block in host_hash_buffer:
                print("File Hash:           ", block)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-p', type=float, help='Percent of file data blocks to sample (hash)')

    parser.add_argument('-b', type=int, help='File block size')

    parser.add_argument('-v', type=int, help='Prints the hash value of each file.')

    parser.add_argument('--device_platform', type=int, help='Device Platform')

    parser.add_argument('--device_class', help='Device Class')

    parser.add_argument('--device_index', type=int, help='Device Index')

    parser.add_argument('--list_devices', help='Lists available OpenCL devices.')

    args = parser.parse_args()

    if args.list_devices:
        print(args)
        platforms = cl.get_platforms()
        for platform in range(0,len(platforms)):

            print("Platform {}: {}".format(platform, platforms[platform].name))

            devices = platforms[platform].get_devices()
            for device in range(0,len(devices)):

                print("Device {}: {}".format(device, devices[device].name))
    else:
        if args.p:
            sample_pct = args.p
        else:
            sample_pct = 1
        if args.v:
            verbose = True
        else:
            verbose = False
        # execute only if run as a script
        OpenCL_Hash(file_block_size=args.b, device_class=args.device_class, device_index=args.device_index, platform_index=args.device_platform).main(sample_percent=sample_pct, verbose=verbose)