# TinyTuya Example
# -*- coding: utf-8 -*-
"""
TinyTuya - Example script that uses the snapshot.json to manage Tuya Devices

Author: Jason A. Cox
For more information see https://github.com/jasonacox/tinytuya
"""

import tinytuya
import json
import time

with open('snapshot.json') as json_file:
    data = json.load(json_file)

#if 'dps' in data['devices'][9]['devId']:
#    print(True)
#else:
#    print(False)    

# Print a table with all devices
#print("%-25s %-24s %-16s %-17s %-5s" % ("Name","ID", "IP","Key","Version"))
for item in data["devices"]:
        name = item["name"]
        print(name)
        id = item["id"]
        print(id)
        ip = item["ip"]
        print(ip)
        key = item["key"]
        print(key)
        ver = item["ver"]
        print(ver)
        #dps = item["dps"]
        #print(dps)

"""def func1(data):
    for key,value in data.items():
        print (str(key)+'->'+str(value))
        if isinstance(value, dict):
            func1(value)
        elif isinstance(value, list):
            for val in value:
                if isinstance(val, str):
                    pass
                elif isinstance(val, list):
                    pass
                else:
                    func1(val)
func1(data)

# Print status of everything
for item in data["devices"]:
    print("\nDevice: %s" % item["name"])
    d = tinytuya.OutletDevice(item["id"], item["ip"], item["key"])
    d.set_version(float(item["ver"]))
    status = d.status()  
    print(status)

# Turn on a device by name
def turn_on(name):
    # find the right item that matches name
    for item in data["devices"]:
        if item["name"] == name:
            break
    print("\nTurning On: %s" % item["name"])
    d = tinytuya.OutletDevice(item["id"], item["ip"], item["key"])
    d.set_version(float(item["ver"]))
    d.set_status(True)

# Turn off a device by name
def turn_off(name):
    # find the right item that matches name
    for item in data["devices"]:
        if item["name"] == name:
            break
    print("\nTurning Off: %s" % item["name"])
    d = tinytuya.OutletDevice(item["id"], item["ip"], item["key"])
    d.set_version(float(item["ver"]))
    d.set_status(False)

# Test it
turn_off('Dining Room')
time.sleep(2)
turn_on('Dining Room')"""

