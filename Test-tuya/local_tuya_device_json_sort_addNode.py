import pandas as pd
import json
import numpy as np

f = open('snapshot.json',)
jsonData = json.load(f) #jsonData = open('snapshot.json',)  #json.loads(jsonData)

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
        address = row['type'] + '_%s' %(idx+1)
        print('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(name=name,
                                                                    id_new=id_new, 
                                                                    ip=ip,
                                                                    key=key,ver=ver,
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
        address = row['type'] + '_%s' %(idx+1)
        
        print('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(name=name,
                                                                    id_new=id_new, 
                                                                    ip=ip,
                                                                    key=key,ver=ver,
                                                                    address=address,))

f.close()