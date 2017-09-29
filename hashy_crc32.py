import numpy as np
import file_handler
import opencl_device
import time

class OpenCL_Hash:

    def __init__(self, file_path="example_data", file_block_size=8192, device_class="GPU", device_index=0, platform_index=0):

        self.file_path = file_path
        self.file_block_size = file_block_size
        self.file_handler = file_handler.FileHandler(self.file_path, self.file_block_size)
        self.device = opencl_device.Device(device_class, device_index, platform_index)

        kernel_variables = {'{{BUFFER_LENGTH}}': file_block_size}
        scalar_vars = [None, None, None, np.int32]

        # Load the kernel
        self.device.load_kernel("kernels/hashy_kernel_crc32.cl", kernel_variables, scalar_vars)

        # Allocate the memory space for the CRC lookup table
        print("Buffer Lookup Table")
        self.host_crc_lookup_table = self.__create_crc_lookup_table()
        self.device_crc_lookup_table = self.buffer_crc_lookup_table(self.host_crc_lookup_table)

        # Allocate the memory space for the resulting CRC hash list
        print("Buffer CRC hash list")
        self.host_crc_hash_list = np.zeros(self.file_handler.set_size, dtype=np.uint)
        self.device_crc_hash_list = self.buffer_crc_hash_list(self.host_crc_hash_list)

    def buffer_file_data_set(self, data_set_buffer):
        return self.device.put_buffer_ro(data_set_buffer)

    def buffer_crc_lookup_table(self, crc_lookup_table):
        return self.device.put_buffer_ro(crc_lookup_table)

    def buffer_crc_hash_list(self, crc_hash_list):
        return self.device.put_buffer_rw(crc_hash_list)

    def hash_data_block_set(self):

        data_set_size = self.file_handler.set_size
        data_block_set = self.file_handler.get_next_block_set()

        # Buffer the block set into the device memory.
        device_data_block_set = self.buffer_file_data_set(data_block_set)

        # Execute the kernel code.
        kernel_execution = self.device.kernel_method(
            self.device.gpu_queue, [self.file_handler.set_size, 1], None,
            device_data_block_set, self.device_crc_lookup_table, self.device_crc_hash_list, data_set_size)

        # Wait for the kernel execution to complete.
        kernel_execution.wait()

        # Release the data blocks that had been allocated to the device.
        device_data_block_set.release()

    def copy_crc_hash_list_from_device(self, device_buffer_ptr, host_buffer):
        self.device.copy_buffer(device_buffer_ptr=device_buffer_ptr, host_buffer=host_buffer)

    def __create_crc_lookup_table(self):
        crc_lookup_table = []

        for i in range(256):
            k = i
            for j in range(8):
                if k & 1:
                    k ^= 0x1db710640
                k >>= 1
            crc_lookup_table.append(k)

        return np.array(crc_lookup_table, dtype=np.uint)

    def main(self):
        start = time.time()
        for i in range(self.file_handler.file_block_count):
            self.hash_data_block_set()

        self.copy_crc_hash_list_from_device(self.device_crc_hash_list, self.host_crc_hash_list)
        end = time.time()
        delta = int((end-start)*1000)

        for crc_hash in self.host_crc_hash_list:
            print("CRC Hash: ", hex(crc_hash))

        print("Time: {}ms".format(delta))
if __name__ == "__main__":
    OpenCL_Hash().main()
