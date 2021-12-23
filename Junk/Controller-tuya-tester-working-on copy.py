
"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey
MIT License
"""
# TreatLife Device Wizard for PolyGlot Node Server Tuya
# -*- coding: utf-8 -*-
# Modules
import requests
import time
import os
import random
import hmac
import hashlib
import json
import tinytuya 

#### TOKEN AUTHENTICATION ####
def tuyaPlatform(apiRegion, apiKey, apiSecret, uri, token=None):
    url = "https://openapi.tuya%s.com/v1.0/%s" % (apiRegion,uri)
    #now = int(time.time()*1000)
    #payload = apiKey + token + str(now)
    now = int(time.time()*1000)
    if(token==None):
        payload = apiKey + str(now)
    else:
        payload = apiKey + token + str(now)
    #print("API Key ", apiKey)
    #print("Token ", payload)
    #print()

    # Sign Payload
    signature = hmac.new(
        apiSecret.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

    # Create Header Data
    headers = {}
    headers['client_id'] = apiKey
    headers['sign_method'] = 'HMAC-SHA256'
    headers['t'] = str(now)
    headers['sign'] = signature
    if(token != None):
        headers['access_token'] = token

    # Get Token
    response = requests.get(url, headers=headers)
    #print("remote response",  response)
    try:
        response_dict = json.loads(response.content.decode())
    except:
        try:
            response_dict = json.loads(response.content)
            print(response_dict)
        except:
            print("Failed to get valid JSON response")
    return(response_dict)

#### Runs First ####
def wizard(response_dict): #color=True
    config = {}
    config['apiKey'] = "txejpdfda9iwmn5cg2es"
    config['apiSecret'] = "46d6072ffd724e0ba5ebeb5cc6b9dce9"
    config['apiRegion'] = 'us'
    config['apiDeviceID'] = "017743508caab5f0973e"
    needconfigs = True
    #SNAPSHOTFILE = 'snapshot.json'

    print('')
    print('TreatLife Device Discovery')  
    print('') 
    print('Authentication' + ' [%s]' % (tinytuya.version))  
    
    if(config['apiKey'] != '' and config['apiSecret'] != '' and
            config['apiRegion'] != '' and config['apiDeviceID'] != ''):
        needconfigs = False
        answer = 'Y' #input(subbold + '    Use existing credentials ' +
                #     normal + '(Y/n): ')
        if('Y'[0:1].lower() == 'n'):
            needconfigs = True

    KEY = config['apiKey']
    SECRET = config['apiSecret']
    DEVICEID = config['apiDeviceID']
    REGION = config['apiRegion']        # us, eu, cn, in
    LANG = 'en'                         # en or zh

    # Get Oauth Token from tuyaPlatform
    uri = 'token?grant_type=1'
    response_dict = tuyaPlatform(REGION, KEY, SECRET, uri)
    token = response_dict['result']['access_token']
    #print(response_dict)

    # Get UID from sample Device ID 
    uri = 'devices/%s' % DEVICEID
    response_dict = tuyaPlatform(REGION, KEY, SECRET, uri, token)
    uid = response_dict['result']['uid']
    

    # Use UID to get list of all Devices for User
    uri = 'users/%s/devices' % uid
    json_data = tuyaPlatform(REGION, KEY, SECRET, uri, token)
    #print("Full json above", json_data)
    #print(json_data)

    # Filter to only Name, ID and Key
    tuyadevices = []
    for i in json_data['result']:
        item = {}
        item['name'] = i['name'].strip()
        item['id'] = i['id']
        item['key'] = i['local_key']
        item['ip'] = i['ip']
        tuyadevices.append(item)

    if('Y'[0:1].lower() != 'n'):
    #### Scan network for devices and provide polling data ####
        #print("\nScanning local network for Tuya devices...\n")
        devices = tinytuya.deviceScan(False, 20) #### changed 20 to 1
        
        def getIP(d, gwid):
            for ip in d:
                if (gwid == d[ip]['gwId']):
                    return (ip, d[ip]['version'])
            return (0, 0)
    #### find devices    
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

    #### Poll for Devices device switches and lights ####
        polling = []
        print("Polling TreatLife Switch Devices...\n")  
        
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
                        #state = alertdim + "Off" + dim
                        try:
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
                                pass
                                result = '1' in data['dps']
                                print(len(result))
                                pass
                                #### here i am trying to add the ID to increment up with the total amount of nodes ####
                                #### need to automate the range to match node total
                                #totalnum = len(name)
                                #print(totalnum)
                                #print("\nPolling TreatLife Switch Devices...\n")
                                #for it in totalnum:
                                #    item['address'] = 'switch_{}'.format(it)
                                #    address = item['address']
                                #    print(item['address'])
                                #pass
                                #### ADDNODE for switch here? ####
                                #node = tuya_switch_node.SwitchNode(self.poly, self.address, address, name, id, ip, key, ver)
                                #self.poly.addNode(node)
                                #self.wait_for_node_done()    

                            else:
                                print("\nPolling TreatLife LED Bulb Devices...\n")
                                if '20' in data['dps']:
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
                                    pass
                                    totalnum = len(ver)
                                    print(totalnum)
                                    for it in range(1, int(totalnum)): #enumerate() '1' in data['dps'] for range
                                        item['address'] = 'light_{}'.format(it)
                                        address = item['address']
                                        print(item['address'])
                                    #### ADDNODE for light here ####    
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
        wizard('response_dict')
    except KeyboardInterrupt:
        pass

    #### Response for switches ####    
    #Polling TreatLife Switch Devices...
    #Switch Family Room Sconces
    #017743508caab5f385a7
    #192.168.1.155
    #7b8f2415ac96dfea
    #3.3
    #Switch Office Outside Lights
    #017743508caab5f0973e
    #192.168.1.145
    #e779c96c964f71b2
    #3.3
    #switch_0
    #Switch0
    #switch_1
    #Switch1

    #Done.

    #### Responce from Lights ###
    #TreatLife Device Discovery

    #Authentication [1.2.6]
    #Polling TreatLife Switch Devices...

    #Garage
    #ebfd4f4263bb769d99zjkq
    #192.168.1.146
    #ec0b2b581a246eab
    #3.3
    #Under Cabinets
    #ebe097c0407da32084kvtr
    #192.168.1.166
    #cb02297ceb692149
    #3.3
    #Office Light
    #ebfc16d57ed374932cjqfk
    #192.168.1.147
    #805217605357161b
    #3.3
    #switch_0
    #Switch0
    #switch_1
    #Switch1

    #Done.

    ####  Device Call 
                            # if '1' in data['dps'] or '20' in data['dps'] or '20' in data['devId']: = All 
                                                            # if '20' in data['dps']: = Lights                                          
                                                            # if '20' in data['devId']: = LED STRIP                                                
                                                            # if '1' in data['dps']: = Switches 
                                                            # 
"""for it in range(0, 6): 
            item['address'] = 'switch_{}'.format(it) #'switch_{}'.format(i) 
            item['title'] = 'Switch {}'.format(it)
            #item['address'] = 'light_{}'.format(it) #'switch_{}'.format(i) 
            #item['title'] = 'Light {}'.format(it)
            pass
            #address = item['address']
            print(item['address'])
            #title =  item['title']
            print(item['title'])

            name = item["name"]
            print(name)
            id = item["id"]
            print(id)
            ip = item["ip"]
            print(ip)
            key = item["key"]
            print(key)
            ver = item["ver"]
            print(ver)"""