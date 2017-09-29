from __future__ import absolute_import, print_function
import pyopencl as cl
import argparse
import hashy_crc32


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

def list_all_devices():
    print(args)
    platforms = cl.get_platforms()
    for platform in range(0, len(platforms)):

        print("Platform {}: {}".format(platform, platforms[platform].name))

        devices = platforms[platform].get_devices()
        for device in range(0, len(devices)):
            print("Device {}: {}".format(device, devices[device].name))

parser = argparse.ArgumentParser()
parser.add_argument('-p', type=float, help='Percent of file data blocks to sample (hash)')
parser.add_argument('-b', type=int, help='File block size')
parser.add_argument('-v', type=int, help='Prints the hash value of each file.')
parser.add_argument('--path', help="The path of the folder to hash")
parser.add_argument('--type', help="The type of hashing you want to perform.")
parser.add_argument('--device_platform', type=int, help='Device Platform')
parser.add_argument('--device_class', help='Device Class')
parser.add_argument('--device_index', type=int, help='Device Index')
parser.add_argument('--list_devices', help='Lists available OpenCL devices.')
args = parser.parse_args()

if args.list_devices:
    list_all_devices()
    exit()

if args.path:
    file_path = args.path
else:
    file_path = "example_data"

if args.p:
    sample_pct = args.p
else:
    sample_pct = 1

if args.b:
    block_size = args.b
else:
    block_size = 8192

if args.v:
    verbose = True
else:
    verbose = False

if args.type:
    hash_type = args.type
else:
    hash_type = "crc32"

if hash_type == "crc32":
    hashy_crc32.OpenCL_Hash(file_path=file_path, file_block_size=block_size, device_class="GPU", device_index=0, platform_index=0).main()
else:
    exit()
