import tinytuya
import json
import pandas as pd
import numpy as np
import time

# scan from tinytuya network

# from file
f = open('snapshot.json',)
devices = json.load(f)
# list = json.dumps(devices, indent=4)
# print(list)

"""devices = tinytuya.deviceScan(False, 20)
# devices = tinytuya.deviceScan(False, 20)
#devices = json.dumps(devices, indent=4)
# print(devices)

# Using Dumps not necessary?
# current = {'timestamp': time.time(), 'devices': scan_results}
output = json.dumps(devices, indent=4)
print("\n JSON \n \n " + output)

for value in devices.value():
    name = ['name']
    ip = value['ip']
    # device_id = value['gwId']
    id = value['id']
    key = value['key']
    dps = value['dps']
    print(name)
    print(ip)
    print(id)
    print(key)
    print(dps)

    #i = 0
    #for i in name:  # for i in iter(lambda: 1+1, -1):
        # address = 'zone_{}'.format(int(i)+1)
    #    address = i+1   # 'zone_{}'.format(int(i))
    #    print(address)
    if "1" in value["dps"]["dps"]:
        print("SWITCH")
        ip = ip[-3:].lstrip('.')
        address = ip

        print(address)
    elif "20" in value["dps"]["dps"]:
        print("LED")
        ip = ip[-3:].lstrip('.')
        address = ip
        print
    else:
        print("OTHER")"""

# devices = tinytuya.deviceScan(False, 20)
# print(devices)
for value in devices.values():
    name = value['name']
    ip = value['ip']
    device_id = value['gwId']
    key = value['key']
    dps = value['dps']
    ip1 = ip[-3:].lstrip('.')
    address = ip1
    # Information
    print(name)
    print(ip)
    print(device_id)
    print(key)
    print(dps)
    """Take the 'dps' status and separates Device types
    Currently a value of '1' is for a switch and'20' LED"""
    if "1" in value["dps"]["dps"]:
        print("SWITCH")
        """node = tuya_switch_node.SwitchNode(
        self.poly, self.address, address, name, device_id, ip, key)
        self.poly.addNode(node)
        self.wait_for_node_done()"""
    elif "20" in value["dps"]["dps"]:
        print("LED")
        """node = tuya_light_node.LightNode(
                self.poly, self.address, address, name, device_id, ip, key)
        self.poly.addNode(node)
        self.wait_for_node_done()"""
    else:
        print("OTHER")


print("Done Appending and sorting")
