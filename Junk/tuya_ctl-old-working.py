"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey / Jason Cox
MIT License
"""
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
        
        #self.Notices.clear()
        default_apiKey = "apiKey"
        default_apiSecret = "apiSecret"
        default_apiRegion = "apiRegion"
        default_apiDeviceId = "apiDeviceId"
        
        self.apiKey = self.Parameters.apiKey
        if self.apiKey is None:
            self.apiKey = default_apiKey
            LOGGER.error('check_params: apiKey not defined in customParams, please add it.  Using {}'.format(default_apiKey))
            self.eapiKey = default_apiKeyself.apiKey = self.Parameters.apiKey

        self.apiSecret = self.Parameters.apiSecret
        if self.apiSecret is None:
            self.apiSecret = default_apiSecret
            LOGGER.error('check_params: apiSecret not defined in customParams, please add it.  Using {}'.format(default_apiSecret))
            self.apiSecret = default_apiSecret

        self.apiRegion = self.Parameters.apiRegion
        if self.apiRegion is None:
            self.apiRegion = default_apiRegion
            LOGGER.error('check_params: apiRegion not defined in customParams, please add it.  Using {}'.format(default_apiRegion))
            self.apiRegion = default_apiRegion
        
        self.apiDeviceId = self.Parameters.apiDeviceId
        if self.apiDeviceId is None:
            self.apiDeviceId = default_apiDeviceId
            LOGGER.error('check_params: apiDeviceId not defined in customParams, please add it.  Using {}'.format(default_apiDeviceId))
            self.apiDeviceId = default_apiDeviceId

    def start(self):
        self.poly.setCustomParamsDoc()
        self.poly.updateProfile()
        self.wait_for_node_done()
        self.LightSwitch(self)

###### Currently Based on snapshot.json needs to be automated #######
    def LightSwitch(self, command):    
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
                address = row['type'] + '_%s' %(idx+1)
                LOGGER.info('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(name=name,
                id_new=id_new, 
                ip=ip,
                key=key,ver=ver,
                address=address,))
                node = tuya_light_node.LightNode(self.poly, self.address, address, name, id_new, ip, key)
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
                address = row['type'] + '_%s' %(idx+1)
                LOGGER.info('{name}\n{id_new}\n{ip}\n{key}\n{ver}\n{address}\n'.format(name=name,
                id_new=id_new, 
                ip=ip,
                key=key,ver=ver,
                address=address,))
                node = tuya_switch_node.SwitchNode(self.poly, self.address, address, name, id_new, ip, key)
                self.poly.addNode(node)
                self.wait_for_node_done()                                                                                                
        f.close()

    def stop(self):
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)

        self.poly.stop()

    def noop(self, command):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}
