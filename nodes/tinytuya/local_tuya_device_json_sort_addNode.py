import tinytuya
import pandas as pd
import json
import numpy as np

#
devices = tinytuya.deviceScan(False, 20)
print(devices)


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
    if "1" in value["dps"]["dps"]:
        print("SWITCH")
    elif "20" in value["dps"]["dps"]:
        print("LED")
    else:
        print("OTHER")

# f = open('snapshot.json',)
# jsonData = open('snapshot.json',)  #json.loads(jsonData)
# jsonData = json.load(f)

# df = pd.json_normalize(jsonData)  # ['devices']
"""df = pd.DataFrame(jsonData['devices'])
df = df.fillna(-1)
print(df)
df['type'] = None
df['type'] = np.where(df['dps.dps.20'] != -1, 'light', df['type'])
df['type'] = np.where(df['dps.1'] != -1, 'switch', df['type'])

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
        print('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(name=name,
                                                                         id_new=id_new,
                                                                         ip=ip,
                                                                         key=key, ver=ver,
                                                                         address=address,))
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

        print('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(name=name,
                                                                         id_new=id_new,
                                                                         ip=ip,
                                                                         key=key, ver=ver,
                                                                         address=address,))

f.close()"""
