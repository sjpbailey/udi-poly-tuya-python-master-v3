import pandas as pd
import json
import numpy as np
import os
import time
import asyncio

import tuya_device_import

# def sendCred(self, command):
##### write config settings for Wizard to 'tinytuya.json' ####

CONFIGFILE = 'tinytuya.json'
print('')
config = {}
config['apiKey'] = "txejpdfda9iwmn5cg2es"
config['apiSecret'] = "46d6072ffd724e0ba5ebeb5cc6b9dce9"
config['apiDeviceID'] = "ebfc16d57ed374932cjqfk"
config['apiRegion'] = "us"
# Write Config
json_object = json.dumps(config, indent=4)
with open(CONFIGFILE, "w") as outfile:
    outfile.write(json_object)
    print(">> Configuration Data Saved to " + CONFIGFILE)
    print(json_object)
os.system("tuya_device_import.py")
exec(open("tuya_device_import.py").read())
print("Gathering Devices Please be Patient")
# time.sleep(50)


f = open('snapshot.json',)
if f is not None:
    # jsonData = open('snapshot.json',)  #json.loads(jsonData)
    jsonData = json.load(f)

df = pd.json_normalize(jsonData['devices'])
df = df.fillna(-1)

df['type'] = None
df['type'] = np.where(df['devId.dps.20'] != -1, 'light', df['type'])
df['type'] = np.where(df['devId.dps.1'] != -1, 'switch', df['type'])

lights = df[df['type'] == 'light'].reset_index(drop=True)
switches = df[df['type'] == 'switch'].reset_index(drop=True)

device_list = [lights]
for device in device_list:
    for idx, row in device.iterrows():
        name = row['name']
        id = row['id']
        id_new = id
        ip = row['ip']
        key = row['key']
        ver = row['ver']
        address = row['type'] + '_%s' % (idx+1)
        print('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(
            name=name, id_new=id_new, ip=ip, key=key, ver=ver, address=address,))
device_list = [switches]
for device in device_list:
    for idx, row in device.iterrows():
        name = row['name']
        id = row['id']
        id_new = id
        ip = row['ip']
        key = row['key']
        ver = row['ver']
        address = row['type'] + '_%s' % (idx+1)

        print('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(
            name=name, id_new=id_new, ip=ip, key=key, ver=ver, address=address,))

f.close()
