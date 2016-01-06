#include "stdafx.h"

#include <windows.h>
#include <psapi.h>
#include <stdio.h>
#include "DriverEnumerate.h"
// To ensure correct resolution of symbols, add Psapi.lib to TARGETLIBS
// and compile with -DPSAPI_VERSION=1

int _tmain(int argc, _TCHAR* argv[])
{

	if (argc < 2){
		_tprintf(TEXT("Usage: ./DriverEnumerate.exe\n"));
		_tprintf(TEXT("\t-l = list drivers\n"));
		_tprintf(TEXT("\t-e $driver_name = examine driver details.\n"));
		_tprintf(TEXT("\t-c $code = convert IOCTL code to definition.\n"));
		_tprintf(TEXT("\t-b $driver_name = bruteforce IOCTLS for a driver.\n"));
		return 1;
	}

	TCHAR* command = argv[1];
	if (_tcscmp(command,TEXT("-l")) == 0){
		printf("Listing drivers.\n");
		ListDrivers();
	} else if (_tcscmp(command, TEXT("-e")) == 0) {
		if (argc < 3) {
			printf("Must specify a valid driver name to examine.\n");
		}
		printf("Examining driver %s\n", argv[2]);
		ExamineDriver(argv[2]);
	} else if (_tcscmp(command, TEXT("-b")) == 0) {
		if (argc < 3){
			printf("Must specify a valid driver name to examine.\n");
		}
		printf("Examining driver %s\n", argv[2]);
		BruteforceCodes(argv[2]);
	} else if (_tcscmp(command, TEXT("-c")) == 0) {
		if (argc < 3){
			printf("Must specify a valid driver name to examine.\n");
		}
		_tprintf(TEXT("Converting: %s\n"), argv[2]);
		long code_int = _tcstol(argv[2], NULL, 16);
		ConvertCode(code_int);
	} else {
		printf("Invalid command.\n");
		return 1;
	}

	return 0;
}

void ListDrivers(void){
	LPVOID drivers[ARRAY_SIZE];
	DWORD cbNeeded;
	int cDrivers, i;

	if (EnumDeviceDrivers(drivers, sizeof(drivers), &cbNeeded) && cbNeeded < sizeof(drivers))
	{
		TCHAR szDriver[ARRAY_SIZE];

		cDrivers = cbNeeded / sizeof(drivers[0]);

		_tprintf(TEXT("There are %d drivers:\n"), cDrivers);
		for (i = 0; i < cDrivers; i++)
		{
			if (GetDeviceDriverBaseName(drivers[i], szDriver, sizeof(szDriver) / sizeof(szDriver[0])))
			{
				_tprintf(TEXT("%d: %s\n"), i, szDriver);
			}
		}
	}
	else
	{
		_tprintf(TEXT("EnumDeviceDrivers failed; array size needed is %d\n"), cbNeeded / sizeof(LPVOID));
	}
}

void GetDriverPath(TCHAR *driverName, TCHAR* path){
	LPVOID drivers[ARRAY_SIZE];
	DWORD cbNeeded;
	int cDrivers, i;

	if (EnumDeviceDrivers(drivers, sizeof(drivers), &cbNeeded) && cbNeeded < sizeof(drivers))
	{
		TCHAR szDriver[ARRAY_SIZE];

		cDrivers = cbNeeded / sizeof(drivers[0]);

		for (i = 0; i < cDrivers; i++)
		{
			if (GetDeviceDriverBaseName(drivers[i], szDriver, sizeof(szDriver) / sizeof(szDriver[0])))
			{
				if (_tcscmp(szDriver, driverName) == 0){
					break;
				}
			}
		}
		TCHAR driverPath[ARRAY_SIZE];
		if (GetDeviceDriverFileName(drivers[i], driverPath, sizeof(driverPath) / sizeof(driverPath[0]))){
			_tcscpy_s(path, ARRAY_SIZE, driverPath);
		}
	}
	else
	{
		_tprintf(TEXT("EnumDeviceDrivers failed; array size needed is %d\n"), cbNeeded / sizeof(LPVOID));
	}
}

void ExamineDriver(TCHAR *name){
	TCHAR path[ARRAY_SIZE];
	GetDriverPath(name,path);
	_tprintf(TEXT("Driver path is %s.\n"), path);
}

TCHAR * MethodFromIOCTL(unsigned int code){
	unsigned int index = code & 3;
	if (index >= METHOD_COUNT){
		_tprintf(_T("Invalid code - cannot calculate method."));
	}
	return methods[index];
}

TCHAR * AccessFromIOCTL(unsigned int code){
	unsigned int index = ((code & 0xC000) >> 14);
	if (index >= ACCESS_COUNT){
		_tprintf(_T("Invalid code - cannot calculate access."));
	}
	return access[index];
}

TCHAR * DeviceFromIOCTL(unsigned int code){
	unsigned int index = ((code & 0xffff0000) >> 16) - 1;
	if (index >= DEVICE_TYPE_COUNT){
		_tprintf(_T("Invalid code - cannot calculate method."));
	}
	return device_types[index];
}

unsigned int FunctionFromIOCTL(unsigned int code){
	return (code & 0x3FFC) >> 2;
}

void ConvertCode(unsigned int code){
	TCHAR* method = MethodFromIOCTL(code);
	TCHAR* access = AccessFromIOCTL(code);
	TCHAR* device_type = DeviceFromIOCTL(code);
	unsigned int function = FunctionFromIOCTL(code);
	_tprintf(_T("Method: %s\n"), method);
	_tprintf(_T("Access: %s\n"), access);
	_tprintf(_T("Device Type: %s\n"), device_type);
	_tprintf(_T("Funcion: 0x%x\n"), function);
	_tprintf(_T("#define NAME CTL_CODE(%s,0x%x,%s,%s)\n"),device_type,function,method,access);
}

void BruteforceCodes(TCHAR* name){
	_tprintf(TEXT("Bruteforcing driver IOCTLS for %s.\n"), name);
	TCHAR path[ARRAY_SIZE];
	GetDriverPath(name, path);
	_tprintf(TEXT("Driver path is %s.\n"), path);
	HANDLE hDevice = CreateFile(_T("\\\\.\\HackSysExtremeVulnerableDriver"), GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL | FILE_FLAG_OVERLAPPED, 0);
	if (hDevice == NULL){
		_tprintf(_T("Could not open device handle.\n"));
		return;
	}
	_tprintf(TEXT("Device HANDLE opened, starting bruteforce.\n"));
	unsigned int ioctl;
	for (int d = 0; d < DEVICE_TYPE_COUNT; d++){
		for (int f = 0; f < MAX_FUNCTION_CODE; f++){
			for (int m = 0; m < METHOD_COUNT; m++){
				for (int a = 0; a < ACCESS_COUNT; a++){
					ioctl = CTL_CODE(d, f, m, a);
					__try {
						bool success = DeviceIoControl(
							hDevice,
							ioctl,
							NULL,
							0,
							NULL,
							0,
							NULL,
							NULL
							);
						if (!success){
							printf("Found\n");
						}
					}
					__except (EXCEPTION_EXECUTE_HANDLER) {
						printf("IOCTL: 0x%x caused an exception!\n", ioctl);
						ConvertCode(ioctl);
					}
					//printf("%s\n", success ? "true" : "false");
				}
			}
		}
	}
}