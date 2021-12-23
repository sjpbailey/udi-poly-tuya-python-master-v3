"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey
MIT License
"""
import udi_interface
import sys
import time
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from enum import Enum
import requests
import time
import os
import random
import hmac
import hashlib
import json
import tinytuya

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
        
        ## Switch Node Paramerter
        if self.Parameters['switchnodes'] is not None:
            if int(self.Parameters['switchnodes']) > 0:
                validSwitches = True
            else:
                LOGGER.error('Invalid number of switc hnodes {}'.format(self.Parameters['switchnodes']))
        else:
            LOGGER.error('Missing number of switch nodes parameter')

        if validSwitches:
            self.createSwitches(int(self.Parameters['switchnodes']))
            self.poly.Notices.clear()
        else:
            self.poly.Notices['switchnodes'] = 'Please configure the number of switch nodes to create.'
            return

        ## Light Node Parameter
        if self.Parameters['lightnodes'] is not None:
            if int(self.Parameters['lightnodes']) > 0:
                validLights = True
            else:
                LOGGER.error('Invalid number of light nodes {}'.format(self.Parameters['lightnodes']))
        else:
            LOGGER.error('Missing number of light nodes parameter')

        if validLights:
            self.createLights(int(self.Parameters['lightnodes']))
            self.poly.Notices.clear()
        else:
            self.poly.Notices['lightnodes'] = 'Please configure the number of light nodes to create.'    
            return
    
    def start(self):
        self.poly.setCustomParamsDoc()
        self.poly.updateProfile()
        self.wait_for_node_done()

    def createSwitches(self, how_many):
        # delete any existing nodes
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                pass
                #self.poly.delNode(node)

        LOGGER.info('Creating {} Switch Nodes'.format(how_many))
        for i in range(0, how_many):
            address = 'switch_{}'.format(i)
            name = 'Switch {}'.format(i) 

            id1 = self.Parameters.id1 
            LOGGER.info(id1)
            ip1 = self.Parameters.ip1
            LOGGER.info(ip1)
            key1 = self.Parameters.key1
            LOGGER.info(key1)

            id2 = self.Parameters.id2 
            LOGGER.info(id2)
            ip2 = self.Parameters.ip2
            LOGGER.info(ip2)
            key2 = self.Parameters.key2
            LOGGER.info(key2)
            
            node = tuya_switch_node.SwitchNode(self.poly, self.address, address, name, id1, ip1, key1, id2, ip2, key2)
            self.poly.addNode(node)
            self.wait_for_node_done()

    def createLights(self, how_many):
        # delete any existing nodes
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                pass
                #self.poly.delNode(node)

        LOGGER.info('Creating {} Light Nodes'.format(how_many))
        for i in range(0, how_many):
            address = 'light_{}'.format(i)
            name = 'Light {}'.format(i) 

            id3 = self.Parameters.id3 
            LOGGER.info(id3)
            ip3 = self.Parameters.ip3
            LOGGER.info(ip3)
            key3 = self.Parameters.key3
            LOGGER.info(key3)

            id4 = self.Parameters.id4 
            LOGGER.info(id4)
            ip4 = self.Parameters.ip4
            LOGGER.info(ip4)
            key4 = self.Parameters.key4
            LOGGER.info(key4)
            
            node1 = tuya_light_node.LightNode(self.poly, self.address, address, name, id3, ip3, key3, id4, ip4, key4)
            self.poly.addNode(node1)
            self.wait_for_node_done()        

    def stop(self):
        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)

        self.poly.stop()

    def query(self,command=None):
        self.reportDrivers()

    commands = {'DISCOVER': query}
