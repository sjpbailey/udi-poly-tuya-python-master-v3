"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey / Jason Cox
MIT License
"""
# For gathering json tinytuya and snapshot by running Wizard as a separate file
# Cannot write json to file or memory (evidently do not know how
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
            self.eapiKey = default_apiKey.apiKey = self.Parameters.apiKey

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

    # class bc:
    #    def __init__(self, sIpAddress, ePlatform):
    #        self.bc = Device()
    #        self.ePlatform = ePlatform
    # class tuyaPlatform:
    #    def __init__(self.apiRegion, self.apiKey, self.apiSecret)

        #### Write Credentials ####
        # time.sleep(5)
        LOGGER.info("Gathering Devices Please be Patient")
        #tuyaPlatform(self, self.apiSecret, self.apiKey, self.apiRegion)
        token = None
        headers = None
        body = None
        apiRegion = self.apiRegion
        apiKey = self.apiKey
        apiSecret = self.apiSecret
        uri = "token?grant_type = 1",
        new_sign_algorithm = True
        tuyaPlatform = self.apiRegion, self.apiKey, self.apiSecret, uri
        ###### Authentication to Tuya Site ######
        LOGGER.info(f"APIKey: {apiKey}")
        uri = "token?grant_type = 1"
        url = "https://openapi.tuya%s.com/v1.0/%s" % (apiRegion, uri)
        now = int(time.time()*1000)
        headers = dict(list(headers.items(
        )) + [('Signature-Headers', ":".join(headers.keys()))]) if headers else {}
        if (token == None):
            payload = str(self.apiKey) + str(now)
            LOGGER.info(f"Payload {payload}")
            headers['secret'] = apiSecret
        else:
            payload = str(self.apiKey) + str(token) + str(now)
        # If running the post 6-30-2021 signing algorithm update the payload to include it's data
        if new_sign_algorithm:
            payload += ('GET\n' +                                                                # HTTPMethod
                        # Content-SHA256
                        hashlib.sha256(bytes((body or "").encode('utf-8'))).hexdigest() + '\n' +
                        ''.join(['%s:%s\n' % (key, headers[key])                                   # Headers
                                for key in headers.get("Signature-Headers", "").split(":")
                                if key in headers]) + '\n' +
                        '/' + url.split('//', 1)[-1].split('/', 1)[-1])
        LOGGER.info('Payload Sent\n' + str(payload))
        # Sign Payload
        signature = hmac.new(
            apiSecret.encode('utf-8'),
            msg=payload.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest().upper()
        # Create Header Data
        headers['client_id'] = apiKey
        LOGGER.info(headers['client_id'])
        headers['sign'] = signature
        headers['t'] = str(now)
        headers['sign_method'] = 'HMAC-SHA256'
        if (token != None):
            headers['access_token'] = token
        LOGGER.info('Headers\n' + str(headers))
        # Get Token
        response = requests.get(url, headers)
        LOGGER.info(f"Token: {response}")
        try:
            response_dict = json.dumps(response.content.decode())
        except:
            try:
                response_dict = json.dumps(response.content)
                # print(response_dict)
            except:
                LOGGER.info("Failed to get valid JSON response")
            return (response_dict)

        config = {}
        config['apiKey'] = self.apiKey
        config['apiSecret'] = self.apiSecret
        config['apiRegion'] = 'us'
        config['apiDeviceID'] = self.apiDeviceId
        needconfigs = False
        if config['apiKey'] == '':
            LOGGER.info('PLEASE ADD YOUR CREDENTIALS')
        # First Message
        LOGGER.info('TinyTuya Device Appender ' +
                    ' [%s]' % (tinytuya.version))
        LOGGER.info('')

        if (config['apiKey'] != '' and config['apiSecret'] != '' and
                config['apiRegion'] != '' and config['apiDeviceID'] != ''):
            needconfigs = False
            # Second Message
            LOGGER.info("    " + "Existing settings:" + "\nAPI Key=%s \nSecret=%s\nDeviceID=%s\n Region=%s" %
                        (config['apiKey'], config['apiSecret'], config['apiDeviceID'], config['apiRegion']))
            # Append Config
            json_object = config  # json.dumps(config, indent=4)
            LOGGER.info(json_object)

            KEY = config['apiKey']
            SECRET = config['apiSecret']
            DEVICEID = config['apiDeviceID']
            REGION = config['apiRegion']
            LANG = 'en'             # us, eu, cn, in
            # en or zh

            # Get Oauth Token from tuyaPlatform
            uri = 'token?grant_type=1'
            # Tuyaplatform(REGION, KEY, SECRET, uri)
            ######## CURRENTLY HERE IN THE SCRIPT LINE 217 THE PLATFORM USED TO BE THE WIZARD FUNCTION ######
            response_dict = tuyaPlatform([REGION, KEY, SECRET, uri])
            LOGGER.info(f"RESPONSE DICT ACCESS TOKEN 1: {response_dict}")
            LOGGER.info(f"RESPONSE DICT ACCESS TOKEN 2: {response_dict[0:5]}")
            if not response_dict[0]:  # ['success']:
                LOGGER.info('\n\n' 'Error from Tuya server: ' +
                            response_dict['msg'])
                pass
            token = response_dict  # ['result']['access_token']

            # Get UID from sample Device ID
            uri = 'devices/%s' % DEVICEID
            response_dict = (REGION, KEY, SECRET, uri, token)
            LOGGER.info(response_dict)
            # if not response_dict['success']:
            #    LOGGER.info('\n\n' + 'Error from Tuya server: ' +
            #                response_dict['msg'])
            #    pass
            uid = response_dict[0]  # ['uid']  # ['result']['uid']
            LOGGER.info(uid)
            # Use UID to get list of all Devices for User
            # 'users/%s/devices' % uid
            # (f"{'users'}", f"{'devices'}", uid)
            uri = 'users/%s/devices' % uid
            json_data = (REGION, KEY, SECRET, uri, token)
            LOGGER.info(json_data)
            # Here internet IP address everything
            output = json.dumps(json_data, indent=4)
            LOGGER.info(f"\nFuture Cloud Control json: {output}\n")
            # Filter to only Name, ID and Key
            """tuyadevices = []
            for i in json_data['result']:  # for i in json_data['result']:
                item = {}
                item['name'] = i['name'].strip()
                item['id'] = i['id']
                item['key'] = i['local_key']
                tuyadevices.append(item)
            # Display device list
            output = json.dumps(tuyadevices, indent=4)  # sort_keys=True')
            LOGGER.info("\n\n" + "Device Listing\n")
            LOGGER.info(output)
            # Scan network for devices and provide polling data
            #LOGGER.info("\nScanning local network for Tuya devices...")

            devices = tinytuya.deviceScan(False, 20)
            def getIP(d, gwid):
                for ip in d:
                    if 'gwId' in d[ip]:
                        if (gwid == d[ip]['gwId']):
                            return (ip, d[ip]['version'])
                return (0, 0)
            polling = []
            LOGGER.info("Polling local devices...")
            for i in tuyadevices:
                item = {}
                name = i['name']
                (ip, ver) = getIP(devices, i['id'])
                item['name'] = name
                item['ip'] = ip
                item['ver'] = ver
                item['id'] = i['id']
                item['key'] = i['key']
                if (ip == 0):
                    LOGGER.info(
                        "    %s[%s] - %s%s - %sError: No IP found%s" % (name, ip, ))
                else:
                    try:
                        d = tinytuya.OutletDevice(i['id'], ip, i['key'])
                        if ver == "3.3":
                            d.set_version(3.3)
                        data = d.status()
                        if 'dps' in data:
                            item['dps'] = data
                            state = "Off"
                            try:
                                if '1' in data['dps'] or '20' in data['dps']:
                                    if '1' in data['dps']:
                                        if data['dps']['1'] == True:
                                            state = "On"
                                    if '20' in data['dps']:
                                        if data['dps']['20'] == True:
                                            state = "On"
                                    # LOGGER.info("    %s[%s] - %s%s - %s - DPS: %r" %
                                    #     (name, ip, state, data['dps']))
                                else:
                                    # LOGGER.info("    %s[%s] - %s%s - DPS: %r" %
                                    #      (name, ip, data['dps']))
                                    pass
                            except:
                                # LOGGER.info("    %s[%s] - %s%s - %sNo Response" %
                                #      (name, ip))
                                pass
                        else:
                            # LOGGER.info("    %s[%s] - %s%s - %sNo Response" %
                            #      (name, ip,))
                            pass
                    except:
                        # LOGGER.info("    %s[%s] - %s%s - %sNo Response" %
                        #      (name, ip))
                        pass
                polling.append(item)
                # for loop
            # Save polling data snapsot
            current = {'timestamp': time.time(), 'devices': polling}
            output1 = json.dumps(current, indent=4)  # indent=4
            # LOGGER.info(f"Local Device json {output1}")
            ###### Sort And ADDNODES #######
            #LOGGER.info('\nThis is POLLED Add DPS sorter here\n')
            df = pd.read_json(output1)
            df = pd.json_normalize(df['devices'])  # Works with Tuple Inserted
            df = df.fillna(-1)
            # LOGGER.info(f"DF: {df}")
            df['type'] = None
            try:
                df['type'] = np.where(
                    df['dps.dps.20'] != -1, 'light', df['type'])
            except:
                pass
            try:
                df['type'] = np.where(
                    df['dps.dps.1'] != -1, 'switch', df['type'])
            except:
                pass
            try:
                df['type'] = np.where(df['dps.101'] != -1, 'tuya', df['type'])
            except:
                pass
            lights = df[df['type'] == 'light'].reset_index(drop=True)
            LOGGER.info(f"\nLIGHTS: {lights}\n")
            switches = df[df['type'] == 'switch'].reset_index(drop=True)
            LOGGER.info(f"\nSWITCHES: {switches}\n")
            tuya = df[df['type'] == 'tuya'].reset_index(drop=True)
            LOGGER.info(f"\nSWITCHES Tuya: {tuya}\n")
            LOGGER.info('\nSort POLLED and Add Nodes\n')
            device_list = [lights]
            for device in device_list:
                for idx, row in device.iterrows():
                    name = row['name']
                    id = row['id']
                    id_new = id
                    ip = row['ip']
                    key = row['key']
                    ver = row['ver']
                    # id_new = id
                    address = row['type'] + '_%s' % (idx+1)
                    LOGGER.info('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(
                        name=name, id_new=id_new, ip=ip, key=key, ver=ver, address=address,))
                    node = tuya_light_node.LightNode(
                        self.poly, self.address, address, name, id_new, ip, key)
                    self.poly.addNode(node)
                    self.wait_for_node_event()
            device_list = [switches]
            for device in device_list:
                for idx, row in device.iterrows():
                    name = row['name']
                    id = row['id']
                    id_new = id
                    ip = row['ip']
                    key = row['key']
                    ver = row['ver']
                    # id_new = id
                    address = row['type'] + '_%s' % (idx+1)
                    LOGGER.info('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(
                        name=name, id_new=id_new, ip=ip, key=key, ver=ver, address=address,))
                    node = tuya_switch_node.SwitchNode(
                        self.poly, self.address, address, name, id_new, ip, key)
                    self.poly.addNode(node)
                    self.wait_for_node_event()"""

            """device_list = [tuya]
            for device in device_list:
                for idx, row in device.iterrows():
                    name = row['name']
                    id = row['id']
                    id_new = id
                    ip = row['ip']
                    key = row['key']
                    ver = row['ver']
                    # id_new = id
                    address = row['type'] + '_%s' % (idx+1)
                    LOGGER.info('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(
                        name=name, id_new=id_new, ip=ip, key=key, ver=ver, address=address,))
                    node = TuyaNode(
                        self.poly, self.address, address, name, value)
                    self.poly.addNode(node)
                    self.wait_for_node_event()"""

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
