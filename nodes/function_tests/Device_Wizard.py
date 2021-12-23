import requests
import time
import hmac
import hashlib
import json
import tinytuya
import itertools
import pandas as pd
import json
import numpy as np


def tuyaPlatform(apiRegion, apiKey, apiSecret, uri, token=None):
    url = "https://openapi.tuya%s.com/v1.0/%s" % (apiRegion, uri)
    now = int(time.time()*1000)
    if(token == None):
        payload = apiKey + str(now)
    else:
        payload = apiKey + token + str(now)
    # print("API Key ", apiKey)
    # print("Token ", payload)
    # print()
    #print(getattr(tuyaPlatform, payload))

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
    # print("remote response",  response)
    try:
        response_dict = json.loads(response.content.decode())
    except:
        try:
            response_dict = json.loads(response.content)
            print(response_dict)
        except:
            print("Failed to get valid JSON response")
    return(response_dict)


def wizard():  # color=True
    # CONFIGFILE = 'tinytuya.json'
    SNAPSHOTFILE = 'snapshot.json'
    config = {}
    config['apiKey'] = "txejpdfda9iwmn5cg2es"
    config['apiSecret'] = "46d6072ffd724e0ba5ebeb5cc6b9dce9"
    config['apiRegion'] = 'us'
    config['apiDeviceID'] = "017743508caab5f0973e"
    needconfigs = True
    try:
        # Load defaults
        with open(CONFIGFILE) as f:
            config = json.load(f)
    except:
        # First Time Setup
        pass

    print('')
    print('TreatLife Device Discovery')
    print('')
    print('Authentication' + ' [%s]' % (tinytuya.version))

    if(config['apiKey'] != '' and config['apiSecret'] != '' and
            config['apiRegion'] != '' and config['apiDeviceID'] != ''):
        needconfigs = False
        answer = 'Y'  # input(subbold + '    Use existing credentials ' +
        #     normal + '(Y/n): ')
        if('Y'[0:1].lower() == 'n'):
            needconfigs = True

    KEY = config['apiKey']
    SECRET = config['apiSecret']
    DEVICEID = config['apiDeviceID']
    REGION = config['apiRegion']        # us, eu, cn, in
    LANG = 'us'                         # en or zh

    # Get Oauth Token from tuyaPlatform
    uri = 'token?grant_type=1'
    response_dict = tuyaPlatform(REGION, KEY, SECRET, uri)
    token = response_dict['result']['access_token']

    # Get UID from sample Device ID
    uri = 'devices/%s' % DEVICEID
    response_dict = tuyaPlatform(REGION, KEY, SECRET, uri, token)
    uid = response_dict['result']['uid']

    # Use UID to get list of all Devices for User
    uri = 'users/%s/devices' % uid
    json_data = tuyaPlatform(REGION, KEY, SECRET, uri, token)
    # print("Full json above", json_data)

    current = {'timestamp': time.time(), 'devices': json_data}
    output = json.dumps(current, indent=4)
    # print(current)
    # print("\n>> " "Saving device snapshot data to " + SNAPSHOTFILE)
    # with open(SNAPSHOTFILE, "w") as data_file:
    #    data_file.write(output)

    tuyadevices = []
    for i in json_data['result']:
        item = {}
        item['name'] = i['name'].strip()
        item['id'] = i['id']
        item['key'] = i['local_key']
        item['ip'] = i['ip']
        tuyadevices.append(item)

    if('Y'[0:1].lower() != 'n'):
        devices = tinytuya.deviceScan(False, 20)  # changed 20 to 1

        def getIP(d, gwid):
            for ip in d:
                if (gwid == d[ip]['gwId']):
                    return (ip, d[ip]['version'])
            return (0, 0)
        polling = []
        print("Polling TreatLife Devices...\n")

        for i in tuyadevices:
            item = {}
            name = i['name']
            (ip, ver) = getIP(devices, i['id'])  # 'id'
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
                        item['devId'] = data
                        # state = alertdim + "Off" + dim
                        try:
                            if '20' in data['dps'] or '20' in data['devId']:
                                pass
                            if '1' in data['dps']:
                                pass
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
        current = {'timestamp': time.time(), 'devices': polling}
        output = json.dumps(current, indent=4)

        jsonData = json.loads(output)
        df = pd.json_normalize(jsonData['devices'])
        df = df.fillna(-1)

        df['type'] = None
        df['type'] = np.where(
            df['devId.dps.20'] != -1, 'light', df['type'])
        df['type'] = np.where(
            df['devId.dps.1'] != -1, 'switch', df['type'])

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

    print("\nDone.\n")
    return


if __name__ == '__main__':

    try:
        pass
        wizard()  # wizard()
    except KeyboardInterrupt:
        pass
