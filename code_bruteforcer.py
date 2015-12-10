import sys
try:
	import win32file
except:
	print "win32file library needed :("
	#sys.exit(1)
from translate import c_define_from_ioctl

max_device_code = 57
max_access_code = 3
max_method_code = 3
max_function_code = 0x1000

#CTL_CODE(t,f,m,a) (((t)<<16)|((a)<<14)|((f)<<2)|(m))
def ctl_code(device_type, function, method, access):
	return (device_type << 16) | (access << 14) | function << 2 | method

if __name__ == "__main__":
	i = 0
	for d in range(1,57):
		for f in range(0,0x1000):
			for m in range(0,4):
				for a in range(0,4):
					#print ctl_code(d,f,m,a)
					print c_define_from_ioctl(ctl_code(d,f,m,a))
					i += 1
	print "Total range: ", i