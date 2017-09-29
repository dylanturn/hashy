import os
import pyopencl as cl

class Device:

    # Setup the device to run a hash job
    def __init__(self, device_type="CPU", device_index=0, platform_index=0, compiler_output=1):

        if device_type == "GPU":
            device_type = cl.device_type.GPU
        else:
            device_type = cl.device_type.CPU

        os.environ['PYOPENCL_COMPILER_OUTPUT'] = str(compiler_output)

        self.mem_flags = cl.mem_flags
        self.platform = cl.get_platforms()
        self.target_device = [self.platform[platform_index].get_devices(device_type=device_type)[device_index]]
        self.device_context = cl.Context(devices=self.target_device)
        self.gpu_queue = cl.CommandQueue(self.device_context)

    def load_kernel(self, kernel_path, kernel_variables, scalar_dtypes=None):

        device_kernel = self.__render_kernel_template(kernel_path, kernel_variables)

        self.kernel_program = cl.Program(self.device_context, device_kernel).build()

        # Create an instance of the kernel's check method.
        self.kernel_method = self.kernel_program.run_kernel

        if scalar_dtypes:
            self.set_scalar_arg_types(scalar_dtypes)

    def set_scalar_arg_types(self, dtypes):
        # Setup the scalar inputs
        self.kernel_method.set_scalar_arg_dtypes(dtypes)

    def device_name(self):
        return self.target_device[0].name

    # Allocate a device input buffer. Returns a pointer to the device memory space.
    def put_buffer_ro(self, buffer):
        return cl.Buffer(self.device_context, self.mem_flags.READ_ONLY | self.mem_flags.COPY_HOST_PTR,
                         hostbuf=buffer)

    # Allocate a device output buffer. Returns a pointer to the device memory space.
    def put_buffer_wo(self, buffer):
        return cl.Buffer(self.device_context, self.mem_flags.WRITE_ONLY | self.mem_flags.COPY_HOST_PTR,
                         hostbuf=buffer)

    # Allocate a device output buffer. Returns a pointer to the device memory space.
    def put_buffer_rw(self, buffer):
        return cl.Buffer(self.device_context, self.mem_flags.READ_WRITE | self.mem_flags.COPY_HOST_PTR,
                         hostbuf=buffer)

    # Copy a device buffer to host memory.
    def copy_buffer(self, device_buffer_ptr, host_buffer):
        cl.enqueue_copy(self.gpu_queue, host_buffer, device_buffer_ptr)

    # Replace the key variables with values in the dictionary.
    def __render_kernel_template(self, kernel_path, arg_dict):
        try:
            with open(kernel_path, 'r') as f:
                hash_kernel = f.read()
                for key in arg_dict:
                    hash_kernel = hash_kernel.replace(key, str(arg_dict[key]))

            return hash_kernel

        except Exception as e:
            print("Exception: ", e)
            return None