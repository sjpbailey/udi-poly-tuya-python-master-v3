"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey / Jason Cox
MIT License
"""
# For gathering json tinytuya and snapshot by running Wizard as a seperate file
# Cannot write json to file or memory (evedently do not know how
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
        #### Write Creditials ####
        # self.putCred(self)
        # time.sleep(5)
        # os.system("tuya_device_import.py")
        # exec(open("tuya_device_import.py").read())
        LOGGER.info("Gathering Devices Please be Patient")
        time.sleep(15)
        # self.discover(self)
        self.LightSwitch(self)

    # added to test from James
    """def discover(self, *args, **kwargs):
        LOGGER.info("Starting Tuya Device Discovery")
        devices_list = json.loads(self.Parameters['devices'])

        LOGGER.info(json.dumps(devices_list))
        scan_results = tinytuya.deviceScan()

        for value in scan_results.values():
            ip = value['ip']
            device_id = value['gwId']
            if len(device_id) > 10:
                device_id = device_id[:10]

            LOGGER.info(f"Device Scan Device IP: {ip}")
            for dict_found in [x for x in devices_list if x["id"] == value['gwId']]:
                value['name'] = dict_found['name']
                value['key'] = dict_found['key']
                device_node = self.poly.getNode(device_id)
                if device_node is None:
                    LOGGER.info(
                        f"Adding Node: {device_id} - {dict_found['name']}")
                    #self.poly.addNode(TuyaNode(self.poly, self.address, device_id, dict_found['name'], value))
                    self.wait_for_node_event()

        LOGGER.info('Finished Tuya Device Discovery')"""


# Add json data for Device Install
    """def putCred(self, command=None):
        ##### write config settings for Wizard to 'tinytuya.json' ####
        CONFIGFILE = 'tinytuya.json'
        LOGGER.info('')
        config = {}
        config['apiKey'] = self.apiKey
        config['apiSecret'] = self.apiSecret
        config['apiDeviceID'] = self.apiDeviceId
        config['apiRegion'] = self.apiRegion
#### Write Credintils to tinytuya.json
        json_object = json.dumps(config, indent=4)
        with open(CONFIGFILE, "w") as data_file:
            data_file.write(json_object)
            LOGGER.info(">> Configuration Data Saved to " + CONFIGFILE)
            LOGGER.info(json_object)
        os.system("tuya_device_import.py")
#### Start tuya_device_import.py to produce snapshot.json
        exec(open("tuya_device_import.py").read())
        LOGGER.info("Gathering Devices Please be Patient")"""

#### Read Devices from snapshot.json produced by tuya_device_import  ####
#### Adds Nodes Lights and Switches for now ####
    def LightSwitch(self, command):
        # delete any existing nodes
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                self.poly.delNode(node)
# needs to be a grab from the internal ip network for local addresses
        f = open('snapshot.json',)
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
                #id_new = id
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
        f.close()

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
