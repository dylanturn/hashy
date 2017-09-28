import os
import pyopencl as cl
import numpy as np
import time

class Device:

    # Setup the device to run a hash job
    def __init__(self, block_size, device_type=cl.device_type.GPU, device_index=1, platform_index=0):
        os.environ['PYOPENCL_COMPILER_OUTPUT'] = '1'

        self.mem_flags = cl.mem_flags

        self.platform = cl.get_platforms()
        self.target_device = [self.platform[platform_index].get_devices(device_type=device_type)[device_index]]
        self.device_context = cl.Context(devices=self.target_device)
        self.gpu_queue = cl.CommandQueue(self.device_context)

        self.buffer_data_ms = 0
        self.kernel_execute_ms = 0
        self.release_buffer_ms = 0

        with open('hashy_kernel.cl', 'r') as f:
            hash_kernel = f.read()
            hash_kernel = hash_kernel.replace('{{STRING_LENGTH}}', str(block_size))

        self.kernel_program = cl.Program(self.device_context, hash_kernel).build()

        # Create an instance of the kernel's check method.
        self.kernel_method = self.kernel_program.load_database

        # Setup the scalar inputs
        self.kernel_method.set_scalar_arg_dtypes([None, None, np.int32])

    def allocate_device_hash_memory(self, data_set_buffer):
        return self.__device_buffer_read_write(data_set_buffer)

    def allocate_device_data_memory(self, data_set_buffer):
        return self.__device_buffer_read_only(data_set_buffer)

    def hash_data_block_set(self, device_hash_set_pointer, data_block_set, data_set_size):

        buffer_data_start = time.time()
        # Buffer the block set into the device memory.
        device_data_blocks = self.__device_buffer_read_only(data_block_set)
        buffer_data_end = time.time()

        kernel_execute_start = time.time()
        # Execute the kernel code.
        kernel_execution = self.kernel_method(
            self.gpu_queue, [data_set_size, 1], None, device_data_blocks, device_hash_set_pointer, data_set_size)

        # Wait for the kernel execution to complete.
        kernel_execution.wait()
        kernel_execute_end = time.time()

        release_buffer_start = time.time()
        # Release the data blocks that had been allocated to the device.
        device_data_blocks.release()
        release_buffer_end = time.time()

        self.buffer_data_ms = self.buffer_data_ms + int((buffer_data_end-buffer_data_start)*1000)
        self.kernel_execute_ms = self.kernel_execute_ms + int((kernel_execute_end-kernel_execute_start)*1000)
        self.release_buffer_ms = self.release_buffer_ms + int((release_buffer_end-release_buffer_start)*1000)

    def copy_hash_set_from_device(self, src_buffer, dest_buffer):
        self.__copy_buffer_from_device(src_buff=src_buffer, dest_buff=dest_buffer)

    def name(self):
        return self.target_device[0].name

    # Allocate a device input buffer. Returns a pointer to the device memory space.
    def __device_buffer_read_only(self, buffer):
        return cl.Buffer(self.device_context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR,
                         hostbuf=buffer)

    # Allocate a device output buffer. Returns a pointer to the device memory space.
    def __device_buffer_write_only(self, buffer):
        return cl.Buffer(self.device_context, self.mem_flags.WRITE_ONLY | self.mem_flags.COPY_HOST_PTR,
                         hostbuf=buffer)

    # Allocate a device output buffer. Returns a pointer to the device memory space.
    def __device_buffer_read_write(self, buffer):
        return cl.Buffer(self.device_context, self.mem_flags.READ_WRITE | self.mem_flags.COPY_HOST_PTR,
                         hostbuf=buffer)

    # Copy a device buffer to host memory.
    def __copy_buffer_from_device(self, src_buff, dest_buff):
        cl.enqueue_copy(self.gpu_queue, dest_buff, src_buff)