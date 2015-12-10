import sys

help = """
You gone fucked up.
"""

device_types = [
	'FILE_DEVICE_BEEP',
	'FILE_DEVICE_CD_ROM',
	'FILE_DEVICE_CD_ROM_FILE_SYSTEM',
	'FILE_DEVICE_CONTROLLER',
	'FILE_DEVICE_DATALINK',
	'FILE_DEVICE_DFS',
	'FILE_DEVICE_DISK',
	'FILE_DEVICE_DISK_FILE_SYSTEM',
	'FILE_DEVICE_FILE_SYSTEM',
	'FILE_DEVICE_INPORT_PORT',
	'FILE_DEVICE_KEYBOARD',
	'FILE_DEVICE_MAILSLOT',
	'FILE_DEVICE_MIDI_IN',
	'FILE_DEVICE_MIDI_OUT',
	'FILE_DEVICE_MOUSE',
	'FILE_DEVICE_MULTI_UNC_PROVIDER',
	'FILE_DEVICE_NAMED_PIPE',
	'FILE_DEVICE_NETWORK',
	'FILE_DEVICE_NETWORK_BROWSER',
	'FILE_DEVICE_NETWORK_FILE_SYSTEM',
	'FILE_DEVICE_NULL',
	'FILE_DEVICE_PARALLEL_PORT',
	'FILE_DEVICE_PHYSICAL_NETCARD',
	'FILE_DEVICE_PRINTER',
	'FILE_DEVICE_SCANNER',
	'FILE_DEVICE_SERIAL_MOUSE_PORT',
	'FILE_DEVICE_SERIAL_PORT',
	'FILE_DEVICE_SCREEN',
	'FILE_DEVICE_SOUND',
	'FILE_DEVICE_STREAMS',
	'FILE_DEVICE_TAPE',
	'FILE_DEVICE_TAPE_FILE_SYSTEM',
	'FILE_DEVICE_TRANSPORT',
	'FILE_DEVICE_UNKNOWN',
	'FILE_DEVICE_VIDEO',
	'FILE_DEVICE_VIRTUAL_DISK',
	'FILE_DEVICE_WAVE_IN',
	'FILE_DEVICE_WAVE_OUT',
	'FILE_DEVICE_8042_PORT',
	'FILE_DEVICE_NETWORK_REDIRECTOR',
	'FILE_DEVICE_BATTERY',
	'FILE_DEVICE_BUS_EXTENDER',
	'FILE_DEVICE_MODEM',
	'FILE_DEVICE_VDM',
	'FILE_DEVICE_MASS_STORAGE',
	'FILE_DEVICE_SMB',
	'FILE_DEVICE_KS',
	'FILE_DEVICE_CHANGER',
	'FILE_DEVICE_SMARTCARD',
	'FILE_DEVICE_ACPI',
	'FILE_DEVICE_DVD',
	'FILE_DEVICE_FULLSCREEN_VIDEO',
	'FILE_DEVICE_DFS_FILE_SYSTEM',
	'FILE_DEVICE_DFS_VOLUME',
	'FILE_DEVICE_SERENUM',
	'FILE_DEVICE_TERMSRV',
	'FILE_DEVICE_KSEC'
]
methods = [
	'METHOD_BUFFERED',
	'METHOD_IN_DIRECT',
	'METHOD_OUT_DIRECT',
	'METHOD_NEITHER'
]
access = [
	'FILE_ANY_ACCESS',
	'FILE_READ_DATA',
	'FILE_WRITE_DATA',
	'FILE_READ_DATA | FILE_WRITE_DATA'
]

#CTL_CODE(t,f,m,a) (((t)<<16)|((a)<<14)|((f)<<2)|(m))
def ctl_code(device_type, function, method, access):
	return (device_type << 16) | (access << 14) | function << 2 | method

def device_source(ioctl):
	if ((ioctl & 0xffff0000) >> 16) < 0x800:
		return "MS"
	return "VENDOR"

def device_from_ioctl(ioctl):
	try:
		return device_types[((ioctl & 0xffff0000) >> 16) - 1]
	except:
		return "Unknown DeviceType"

def method_from_ioctl(ioctl):
	try:
		return methods[(ioctl & 3)]
	except:
		return "Invalid MethodType"

def access_from_ioctl(ioctl):
	try:
		return access[((ioctl & 0xC000) >> 14)]
	except:
		return "Invalid AccessType"

def function_from_ioctl(ioctl):
	return hex(((ioctl & 0x3FFC) >> 2))

def c_define_from_ioctl(ioctl):
	method = method_from_ioctl(ioctl)
	device = device_from_ioctl(ioctl)
	access = access_from_ioctl(ioctl)
	function = function_from_ioctl(ioctl)
	return "#define NAME CTL_CODE(" + device + "," + function + "," + method + "," + access + ")"

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print help
		sys.exit(1)
	mode = sys.argv[1]
	if mode == "c" or mode == "code":
		if len(sys.argv) < 3:
			print help
			sys.exit(1)
		ioctl = int(sys.argv[2],16)
		method = method_from_ioctl(ioctl)
		device = device_from_ioctl(ioctl)
		access = access_from_ioctl(ioctl)
		function = function_from_ioctl(ioctl)
		print "Device = ", device
		print "Device Source = ", device_source(ioctl)
		print "Function = ", function
		print "Method = ", method
		print "Access = ", access
		print "C Define:"
		print "#define NAME CTL_CODE(" + device + "," + function + "," + method + "," + access + ")"
	elif mode == "d" or mode == "dwords":
		if len(sys.argv) < 6:
			print help
			sys.exit(1)
		print ctl_code(int(sys.argv[2],16),int(sys.argv[3],16),int(sys.argv[4],16),int(sys.argv[5],16))
	elif mode == "s" or mode == "strings":
		if len(sys.argv) < 6:
			print help
			sys.exit(1)
		device_code = device_types.index(sys.argv[2]) + 1
		method_code = methods.index(sys.argv[4])
		access_code = access.index(sys.argv[5])
		print hex(ctl_code(device_code,int(sys.argv[3],16),method_code, access_code))
	else:
		print help