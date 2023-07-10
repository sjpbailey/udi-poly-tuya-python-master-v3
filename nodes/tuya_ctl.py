"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey / Jason Cox
MIT License
This node server polls Tuya TreatLife LED's and Switches based on 
'dps' status. The bash first needs to be run on host IPV4 network
host to enable local network conductivity. Parameters for Credentials
do nothing currently and are for future cloud control.
"""
import udi_interface
import time
import tinytuya
import json
# import xml.etree.ElementTree as ET
# from enum import Enum
# import sys
# import requests
# import os
# import random
# import hmac
# import hashlib
# import asyncio

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
    """ Parameter are for future cloud control """

    def parameterHandler(self, params):
        self.Parameters.load(params)
        validSwitches = False
        validLights = False
        default_apiKey = "apiKey"
        default_apiSecret = "apiSecret"
        default_apiRegion = "apiRegion"
        default_apiDeviceId = "apiDeviceId"

        self.apiKey = self.Parameters.apiKey
        if self.apiKey is None:
            self.apiKey = default_apiKey
            LOGGER.error('check_params: apiKey not defined in customParams, please add it.  Using {}'.format(
                default_apiKey))
            self.apiKey = default_apiKey.apiKey = self.Parameters.apiKey

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
        self.createNodes()

    def createNodes(self):
        LOGGER.info("Gathering Devices Please be Patient")
        """Uses Bash run to gather devices for addNode """
        devices_list = json.loads(self.Parameters['devices'])
        devices = tinytuya.deviceScan(False, 20)
        LOGGER.info(devices)
        for value in devices.values():
            name = value['name']
            ip = value['ip']
            device_id = value['gwId']
            key = value['key']
            dps = value['dps']
            ip1 = ip[-3:].lstrip('.')
            address = ip1
            # Information
            LOGGER.info(name)
            LOGGER.info(ip)
            LOGGER.info(device_id)
            LOGGER.info(key)
            LOGGER.info(dps)
            """Take the 'dps' status and separates Device types
            Currently a value of '1' is for a switch and'20' LED"""
            if "1" in value["dps"]["dps"]:
                LOGGER.info("SWITCH")
                node = tuya_switch_node.SwitchNode(
                    self.poly, self.address, address, name, device_id, ip, key)
                self.poly.addNode(node)
                self.wait_for_node_done()
            elif "20" in value["dps"]["dps"]:
                LOGGER.info("LED")
                node = tuya_light_node.LightNode(
                    self.poly, self.address, address, name, device_id, ip, key)
                self.poly.addNode(node)
                self.wait_for_node_done()
            else:
                LOGGER.info("OTHER")

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
