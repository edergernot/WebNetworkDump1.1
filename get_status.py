'''check devicescount, dumpfiles, excelfiles'''
from global_init import *
import os

def number_dump_files():
    num = 0
    try:
        files = os.listdir(DUMP_DIR)
        for file in files:
            if "_command.txt" in file:
                num += 1
        return(num)
    except Exception as e:
        return (0)

def number_excelfiles():
    num = 0
    try:
        files = os.listdir(f"{DUMP_DIR}/parsed")
        for file in files:
            if ".xlsx" in file:
                num += 1
        return(num)
    except Exception as e:
        return (0)

def number_quickdumpfiles():
    num = 0
    try:
        files = os.listdir("./quickcommand")
        for file in files:
            if "quick" in file:
                num += 1
        return(num)
    except Exception as e:
        return (0)

def number_enabled(devices):
    num=0
    for device in devices:
        if device.enabled:
            num += 1
    return(num)

def get_status(devices:list):
    device_count=len(devices)
    number_of_dumpfiles = number_dump_files()
    #number_of_excelfiles = number_excelfiles()
    number_of_quickcommandfiles = number_quickdumpfiles()
    number_of_enabled = number_enabled(devices)
    status={"number_of_dumpfiles":number_of_dumpfiles,
            "number_quickdump_files":number_of_quickcommandfiles,
            "networkdevices":device_count,
            "enableddevices":number_of_enabled}
    return (status)


