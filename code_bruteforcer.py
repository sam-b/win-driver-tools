"""
	Bruteforces valid ioctl codes and provides definitions for them when setup with valid config to send them to a driver.
"""

import sys
import time
try:
	import win32file
except:
	print "win32file library needed :("
	sys.exit(1)
from translate import c_define_from_ioctl
from translate import ctl_code
max_device_code = 57
max_access_code = 3
max_method_code = 3
max_function_code = 0x1000

if __name__ == "__main__":
	hDevice = win32file.CreateFile('\\\\.\\HackSysExtremeVulnerableDriver', win32file.GENERIC_READ | win32file.GENERIC_WRITE, win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE ,None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL | win32file.FILE_FLAG_OVERLAPPED, 0)
	for d in range(1,max_device_code + 1):
		for f in range(0,max_function_code + 1):
			for m in range(0,max_method_code + 1):
				for a in range(0,max_access_code + 1):
					ioctl = ctl_code(d,f,m,a)
					try:
						data = win32file.DeviceIoControl(
							hDevice,
							ioctl,
							'',
							0,
							None
						)
						print "Found ioctl: " + hex(ioctl) + " , C define:"
						print c_define_from_ioctl(ioctl)
					except Exception as e:
						if e[0] == 998:
							print "Found ioctl triggered out of bounds memory access: " + hex(ioctl) + " , C define:"
							print c_define_from_ioctl(ioctl)
						pass