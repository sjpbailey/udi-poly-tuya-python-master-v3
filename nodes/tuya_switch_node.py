"""
Polyglot v3 node server
Copyright (C) 2021 Steven Bailey
MIT License
"""
import udi_interface
import sys
import os
import time
import logging
import tinytuya
import random

LOGGER = udi_interface.LOGGER


class SwitchNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, id_new, ip, key):
        super(SwitchNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address, name)  # address,name
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.id_new = id_new
        self.DEVICEID = id_new
        self.ip = ip
        self.DEVICEIP = ip
        self.key = key
        self.DEVICEKEY = key
        LOGGER.info('{name}\n{id_new}\n{ip}\n{key}\n'.format(
            name=name, id_new=id_new, ip=ip, key=key,))
        self.DEVICEVERS = "us"  # NEED TO WORK OUT SEND FROM CONTROLLER
        self.setDriver('ST', 1)

    def setSwOn(self, command):
        DEVICEID = self.DEVICEID  # DEVICEID = self.DEVICEID
        DEVICEIP = self.DEVICEIP  # DEVICEIP = self.DEVICEIP
        DEVICEKEY = self.DEVICEKEY  # DEVICEKEY = self.DEVICEKEY
        DEVICEVERS = self.DEVICEVERS
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        d = tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.turn_on()
        LOGGER.info('    Turn Switch On')
        self.SwStat(self)

    def setSwOff(self, command):
        DEVICEID = self.DEVICEID
        DEVICEIP = self.DEVICEIP
        DEVICEKEY = self.DEVICEKEY
        DEVICEVERS = self.DEVICEVERS
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        d = tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        LOGGER.info('    Turn Switch Off')
        d.turn_off()
        self.SwStat(self)

    def SwStat(self, command):
        DEVICEID = self.DEVICEID
        DEVICEIP = self.DEVICEIP
        DEVICEKEY = self.DEVICEKEY
        DEVICEVERS = self.DEVICEVERS
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        d = tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        stat = d.status()
        #LOGGER.info('Current Status of Switch: %r' % stat['dps']['1'])
        if stat['dps']['1'] == True:
            self.setDriver('GV2', 1)
        elif stat['dps']['1'] == False:
            self.setDriver('GV2', 0)

    def poll(self, polltype):
        if 'longPoll' in polltype:
            LOGGER.debug('longPoll (node)')
        else:
            self.query(self)
            self.SwStat(self)
            LOGGER.debug('shortPoll (node)')

    def query(self, command=None):
        self.SwStat(self)
        self.reportDrivers()

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV2', 'value': 0, 'uom': 2},
    ]

    id = 'switch'

    commands = {
        'SWTON': setSwOn,
        'SWTOF': setSwOff,
        'QUERY': query
    }
