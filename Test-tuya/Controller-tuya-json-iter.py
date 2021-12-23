"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey
MIT License
"""
# TreatLife Device Wizard for PolyGlot Node Server Tuya
# -*- coding: utf-8 -*-
# Modules
import json
import tinytuya
import itertools
from itertools import count

#### Scan json for devices and provide polling data ####
### Poll for Devices device switches and lights ####
#### Device Call Bottom Switches or Lights or All ####
    # if '1' in data['dps'] or '20' in data['dps'] or '20' in data['devId']: = All
    # if '20' in data['dps']: = Lights
    # if '20' in data['devId']: = LED STRIP
    # if '1' in data['dps']: = Switches

def wizard():
    # Filter to only Name, ID and Key
    f = open('snapshot.json',)
    data = json.load(f)
    tuyadevices = []
    for i in data['devices']:
        item = {}
        item['name'] = i['name'].strip()
        item['id'] = i['id'] 
        item['key'] = i['key']
        item['ip'] = i['ip']
        tuyadevices.append(item)

    if('Y'[0:1].lower() != 'n'):
        print("\nParcing snapshot.json for Tuya Switches...\n")
        devices = tinytuya.deviceScan(False, 20) #### changed 20 to 1
        
        def getIP(d, gwid):
            for ip in d:
                if (gwid == d[ip]['gwId']):
                    return (ip, d[ip]['version'])
            return (0, 0)

        polling = []
        for i in tuyadevices:
            item = {}
            name = i['name']
            (ip, ver) = getIP(devices, i['id'])  ## 'id'
            item['name'] = name
            item['ip'] = ip
            item['ver'] = ver
            item['id'] = i['id']
            item['key'] = i['key']
            if (ip == 0):
                pass
            else:
                try:
                    d = tinytuya.OutletDevice(i['id'], ip, i['key'])
                    if ver == "3.3":
                        d.set_version(3.3)
                    data = d.status()
                    if 'dps' in data:     
                        item['devId']= data    
                        try:
                            ### Add Switches
                            if '1' in data['dps']:
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
                                #count = int(totalnum)
                                return
                                pass
                                totalnum = len(data['dps'])
                                print(totalnum)
                                #count = 0
                                for i in range(0, 10): #for it in seq: #: #range(0, count):
                                    item['address'] = 'switch_{}'.format(i)
                                    print(item['address'])
                                    print("\n")
                                    print(i)
                                    pass

                            ### Add Lights
                            #if '20' in data['dps'] or '20' in data['devId']:
                                #totalnum = len(data['dps'])
                                #name = item["name"]
                                #print(name)
                                #id = item["id"]
                                #print(id)
                                #ip = item["ip"]
                                #print(ip)
                                #key = item["key"]
                                #print(key)
                                #ver = item["ver"]
                                #print(ver)
                                #count = totalnum
                                #pass
                                #for it in range(1, totalnum):
                                #    item['address'] = 'light_{}'.format(it)
                                #print(item['address'])
                                #print("\n")
                                    
                            else:
                                pass
                        except:
                            
                            pass
                    else:
                        pass
                except:
                    pass
                        
            polling.append(item)
            pass

    print("\nDone.\n")
    return

if __name__ == '__main__':

    try:
        pass
        wizard()
    except KeyboardInterrupt:
        pass
