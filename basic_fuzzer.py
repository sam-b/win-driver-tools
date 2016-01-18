"""
	Super basic fuzzer for a single IOCTL at a time.
"""

import sys
import time
import random
from ctypes import *
kernel32 = windll.kernel32

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 0x3
FILE_SHARE_READ = 0x1
FILE_SHARE_WRITE =0x2
FILE_ATTRIBUTE_NORMAL = 0x00000080
FILE_FLAG_OVERLAPPED = 0x40000000
	
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print "Usage: python basic_fuzzer.py DRIVER_PATH_INCLUDING_ESCAPES IOCTL_CODE_IN_HEX"
	ioctl = int(sys.argv[2],16)
	while True:
		try:
			with open('fuzz.log','a+') as log:
				hDevice = kernel32.CreateFileW(sys.argv[1].decode("mbcs"), GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE ,None, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OVERLAPPED, None)
				if hDevice == -1:
					print "Could not open device"
					sys.exit(1)
				in_size = random.randint(0,2 ** 10) 
				if random.random() < 0.5:
					in_buff = ''.join(chr(random.randint(0,255)) for _ in range(in_size))
				else:
					in_buff = ''.join(chr(random.randint(0,255)) for _ in range(random.randint(0,2 ** 16)))
				log.write("in_buff = " + in_buff)
				out_size = random.randint(0,2 ** 10) 
				if random.random() < 0.5:
					out_buff = ''.join(chr(random.randint(0,255)) for _ in range(out_size))
				else:
					out_buff = ''.join(chr(random.randint(0,255)) for _ in range(random.randint(0,2 ** 16)))
				log.write("out_buff = " + out_buff)
				out_length = c_ulong(out_size)
				log.write("kernel32.DeviceIoControl(hDevice," + str(ioctl) + ",in_buff," + str(in_size) + ",out_buff," + str(out_size) + "," + str(out_length) + ", None)")
				print "Executing kernel32.DeviceIoControl(hDevice," + str(ioctl) + ",in_buff," + str(in_size) + ",out_buff," + str(out_size) + "," + str(out_length) + ", None)"
			data = kernel32.DeviceIoControl(
				hDevice,
				ioctl,
				cast(in_buff, c_char_p),
				in_size,
				byref(cast(out_buff, c_char_p)),
				out_size,
				byref(out_length),
				None
			)
		except Exception as e:
			print e