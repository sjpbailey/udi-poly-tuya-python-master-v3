"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey / Jason Cox
MIT License
"""
# For gathering json tinytuya and snapshot by running Wizard within the controller
import udi_interface
import udi_interface
import sys
import time
import xml.etree.ElementTree as ET
from enum import Enum
import requests
import os
import random
import hmac
import hashlib
import tinytuya
import pandas as pd
import numpy as np
import json
import asyncio

from nodes import tuya_switch_node
from nodes import tuya_light_node

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class Controller(udi_interface.Node):
    id = 'ctl'
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 56},
    ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.n_queue = []
        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def parameterHandler(self, params):
        self.Parameters.load(params)
        validSwitches = False
        validLights = False

        # self.Notices.clear()
        default_apiKey = "apiKey"
        default_apiSecret = "apiSecret"
        default_apiRegion = "apiRegion"
        default_apiDeviceId = "apiDeviceId"

        self.apiKey = self.Parameters.apiKey
        if self.apiKey is None:
            self.apiKey = default_apiKey
            LOGGER.error('check_params: apiKey not defined in customParams, please add it.  Using {}'.format(
                default_apiKey))
            self.apiKey = default_apiKey
            self.apiKey = self.Parameters.apiKey

        self.apiSecret = self.Parameters.apiSecret
        if self.apiSecret is None:
            self.apiSecret = default_apiSecret
            LOGGER.error('check_params: apiSecret not defined in customParams, please add it.  Using {}'.format(
                default_apiSecret))
            self.apiSecret = default_apiSecret

        self.apiRegion = self.Parameters.apiRegion
        if self.apiRegion is None:
            self.apiRegion = default_apiRegion
            LOGGER.error('check_params: apiRegion not defined in customParams, please add it.  Using {}'.format(
                default_apiRegion))
            self.apiRegion = default_apiRegion

        self.apiDeviceId = self.Parameters.apiDeviceId
        if self.apiDeviceId is None:
            self.apiDeviceId = default_apiDeviceId
            LOGGER.error('check_params: apiDeviceId not defined in customParams, please add it.  Using {}'.format(
                default_apiDeviceId))
            self.apiDeviceId = default_apiDeviceId

    def start(self):
        self.poly.setCustomParamsDoc()
        self.poly.updateProfile()
        self.wait_for_node_done()
        #### Write Creditials ####
        self.wizard(self, self.apiKey, self.apiSecret,
                    'uri', 'token', 'command')

    def tuyaPlatform(self, apiRegion, apiKey, apiSecret, uri, token=None):
        url = "https://openapi.tuya%s.com/v1.0/%s" % (apiRegion, uri)
        now = int(time.time()*1000)
        if(token == None):
            payload = apiKey + str(now)
        else:
            payload = apiKey + token + str(now)
        LOGGER.info("API Key ", apiKey)
        LOGGER.info("Token ", payload)
        # print()

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

    def wizard(self, REGION, KEY, SECRET, uri, token, command):  # color=True
        tuyaPlatform = None
        CONFIGFILE = 'tinytuya.json'
        # SNAPSHOTFILE = 'snapshot.json'
        config = {}
        config['apiKey'] = self.apiKey  # "txejpdfda9iwmn5cg2es"
        # "46d6072ffd724e0ba5ebeb5cc6b9dce9"
        config['apiSecret'] = self.apiSecret
        config['apiRegion'] = self.apiRegion  # 'us'
        config['apiDeviceID'] = self.apiDeviceId  # "017743508caab5f0973e"
        needconfigs = True
        try:
            # Load defaults
            with open(CONFIGFILE) as f:
                config = json.load(f)
        except:
            # First Time Setup
            pass

        # print('')
        LOGGER.info('TreatLife Device Discovery')
        # print('')
        # print('Authentication' + ' [%s]' % (tinytuya.version))

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
        self.token = response_dict['result']['access_token']

        # Get UID from sample Device ID
        uri = 'devices/%s' % DEVICEID
        response_dict = tuyaPlatform(REGION, KEY, SECRET, uri, token)
        uid = response_dict['result']['uid']

        # Use UID to get list of all Devices for User
        uri = 'users/%s/devices' % uid
        json_data = tuyaPlatform(REGION, KEY, SECRET, uri, token)
        # print("Full json above", json_data)

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
            devices = tinytuya.deviceScan(False, 20)  # changed 20 to 1

            def getIP(d, gwid):
                for ip in d:
                    if (gwid == d[ip]['gwId']):
                        return (ip, d[ip]['version'])
                return (0, 0)
            polling = []
            # print("Polling TreatLife Switch Devices...\n")

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
            # Save polling data snapsot
            current = {'timestamp': time.time(), 'devices': polling}
            output = json.dumps(current, indent=4)

        #### Adds Nodes Lights and Switches for now ####
        output = None
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
                LOGGER.info('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(
                    name=name, id_new=id_new, ip=ip, key=key, ver=ver, address=address,))
                node = tuya_light_node.LightNode(
                    self.poly, self.address, address, name, id_new, ip, key)
                self.poly.addNode(node)
                self.wait_for_node_done()

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
                LOGGER.info('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(
                    name=name, id_new=id_new, ip=ip, key=key, ver=ver, address=address,))
                node = tuya_switch_node.SwitchNode(
                    self.poly, self.address, address, name, id_new, ip, key)
                self.poly.addNode(node)
                self.wait_for_node_done()

    def delete(self):
        LOGGER.info('Delete Tuya Controller.')

    def stop(self):
        self.poly.stop()
        LOGGER.debug('NodeServer stopped.')
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)

    def noop(self, command):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}


if __name__ == '__main__':
    try:
        pass
        #wizard()  # wizard()
        # except KeyboardInterrupt:
        pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
