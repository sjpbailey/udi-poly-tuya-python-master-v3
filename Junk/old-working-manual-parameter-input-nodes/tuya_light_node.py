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

class LightNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, id3, ip3, key3, id4, ip4, key4): #, ip, id1, key1 key, ip, id
        super(LightNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address,name)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        if address == 'light_{}'.format(0):
            self.id3 = id3
            self.DEVICEID = id3
            self.ip3 = ip3
            self.DEVICEIP = ip3
            self.key3 = key3
            self.DEVICEKEY = key3
        elif address == 'light_{}'.format(1):
            self.id4 = id4
            self.DEVICEID = id4
            self.ip4 = ip4
            self.DEVICEIP = ip4        
            self.key4v= key4
            self.DEVICEKEY = key4            
        else:
            pass   
        self.DEVICEVERS = "us"

    #### Light On 
    def setSwOn(self, command):
        DEVICEID = self.DEVICEID
        DEVICEIP = self.DEVICEIP
        DEVICEKEY = self.DEVICEKEY
        DEVICEVERS = self.DEVICEVERS
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        LOGGER.info('    Turn Lamp 1 On')
        d.turn_on()
        self.setDriver('GV2', 1) # add Status Actual

    #### Light Off            
    def setSwOff(self, command):
        DEVICEID = self.DEVICEID
        DEVICEIP = self.DEVICEIP
        DEVICEKEY = self.DEVICEKEY
        DEVICEVERS = self.DEVICEVERS
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)
        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        LOGGER.info('    Turn Lamp 1 Off')
        
        # Turn off
        d.turn_off()
        self.setDriver('GV2', 0)

    #### Test Light 
    def setclrflip(self, command):
        DEVICEID = self.DEVICEID
        DEVICEIP = self.DEVICEIP
        DEVICEKEY = self.DEVICEKEY
        DEVICEVERS = self.DEVICEVERS
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)
        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        
        # Turn on
        d.turn_on()
        self.setDriver('GV2', 1)
        time.sleep(1)

        # Dimmer Test
        LOGGER.info('\nDimmer Control Test')
        for level in range(11):
            LOGGER.info('    Level: %d%%' % (level*10))
            d.set_brightness_percentage(level*10)
            time.sleep(1)

        # Colortemp Test
        LOGGER.info('\nColortemp Control Test (Warm to Cool)')
        for level in range(11):
            LOGGER.info('    Level: %d%%' % (level*10))
            d.set_colourtemp_percentage(level*10)
            time.sleep(1)
        
        # Test by Flipping through colors of rainbow - set_colour(r, g, b):
        LOGGER.info('\nColor Test - Cycle through rainbow')
        rainbow = {"red": [255, 0, 0], "orange": [255, 127, 0], "yellow": [255, 200, 0],
            "green": [0, 255, 0], "blue": [0, 0, 255], "indigo": [46, 43, 95],
            "violet": [139, 0, 255]}
        for x in range(2):
            for i in rainbow:
                r = rainbow[i][0]
                g = rainbow[i][1]
                b = rainbow[i][2]
                LOGGER.info('    %s (%d,%d,%d)' % (i, r, g, b))
                d.set_colour(r, g, b)
                time.sleep(2)
            LOGGER.info('')
            
        # Turn off
        d.turn_off()
        self.setDriver('GV2', 0)
        time.sleep(1)

        # Random Color Test
        d.turn_on()
        LOGGER.info('\nRandom Color Test')
        for x in range(10):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            LOGGER.info('    RGB (%d,%d,%d)' % (r, g, b))
            d.set_colour(r, g, b)
            time.sleep(2)

        # Test Modes
        LOGGER.info('\nTesting Bulb Modes')
        LOGGER.info('    Colour')
        d.set_mode('colour')
        time.sleep(2)
        LOGGER.info('    Scene')
        d.set_mode('scene')
        time.sleep(2)
        LOGGER.info('    Music')
        d.set_mode('music')
        time.sleep(2)
        LOGGER.info('    White')
        d.set_mode('white')
        time.sleep(2)

        # Turn off
        d.turn_on()
        self.setDriver('GV2', 1)
        time.sleep(1)
        LOGGER.info('\nDone')

    # Set Modes
    def modeOn(self, command):
        DEVICEID = self.DEVICEID
        DEVICEIP = self.DEVICEIP
        DEVICEKEY = self.DEVICEKEY
        DEVICEVERS = self.DEVICEVERS
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        self.modeOn = int(command.get('value'))
        self.setDriver('GV4', self.modeOn)
        if self.modeOn == 0:
            d.set_mode('colour')
            LOGGER.info('Colour')
        elif self.modeOn == 1:
            d.set_mode('scene')
            LOGGER.info('Scene')
        elif self.modeOn == 2:
            d.set_mode('music')
            LOGGER.info('Music')
        elif self.modeOn == 3:
            d.set_colour(255,0,0)
            LOGGER.info('Red')
        elif self.modeOn == 4:
            d.set_colour(255,127,0)
            LOGGER.info('Orange')
        elif self.modeOn == 5:
            d.set_colour(255,200,0)
            LOGGER.info('Yellow')
        elif self.modeOn == 6:
            d.set_colour(0,255,0)
            LOGGER.info('Green')
        elif self.modeOn == 7:
            d.set_colour(0,0,255)
            LOGGER.info('Blue')
        elif self.modeOn == 8:
            d.set_colour(46,43,95)
            LOGGER.info('Indigo')
        elif self.modeOn == 9:
            d.set_colour(139,0,255)
            LOGGER.info('Violet')
        elif self.modeOn == 10:
            d.set_mode('white')
            LOGGER.info('White')    
        else:
            pass

    # Led Level
    def setDim(self, command):
        DEVICEID = self.DEVICEID
        DEVICEIP = self.DEVICEIP
        DEVICEKEY = self.DEVICEKEY
        DEVICEVERS = self.DEVICEVERS
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        
        ivr_one = 'percent'
        percent = int(command.get('value'))
        def set_percent(self, command):
            percent = int(command.get('value')*10)
        if percent < 0 or percent > 100:
            LOGGER.error('Invalid Level {}'.format(percent))
        else:
            d.set_brightness_percentage(percent) #d.set_brightness_percentage(percent)            
            self.setDriver('GV3', percent)
            LOGGER.info('Dimmer Setpoint = ' + str(percent) +'Level')

    def poll(self, polltype):
        if 'longPoll' in polltype:
            LOGGER.debug('longPoll (node)')
        else:
            self.query(self)
            LOGGER.debug('shortPoll (node)')

    def query(self,command=None):
        self.reportDrivers()
        
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV2', 'value': 0, 'uom': 2},
            {'driver': 'GV3', 'value': 0, 'uom': 51},
            {'driver': 'GV4', 'value': 0, 'uom': 25},
            
        ]

    id = 'light'

    commands = {
                'LGTON': setSwOn,
                'LGTOF': setSwOff,
                'LGTCFLIP':setclrflip,
                'MODE': modeOn,
                'STLVL': setDim,
                'QUERY': query,
        }
    