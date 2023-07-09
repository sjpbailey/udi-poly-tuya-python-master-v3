import tinytuya
import json
import pandas as pd
import numpy as np
import time

# from file
f = open('snapshot.json',)
devices = json.load(f)


df = pd.DataFrame(devices)
df = df.fillna(-1)
print(df)
# print(df.index, df['dps.dps.20'])

ip1 = '192.168.1.10'
ip2 = '192.168.1.100'
print(ip1[-3:].lstrip('.'))

print(ip2[-3:].lstrip('.'))
