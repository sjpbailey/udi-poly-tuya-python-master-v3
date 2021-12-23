#!/usr/bin/env python
try:
    import polyinterface
    from polyinterface import Controller,LOG_HANDLER,LOGGER
except ImportError:
    import pgc_interface as polyinterface
import sys
import time
import os
import requests
import hmac
import hashlib
import json
import pprint
import logging
import tinytuya
import random 
#from tinttuya import tuyaPlatform


LOGGER = polyinterface.LOGGER
# IF you want a different log format than the current default
LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')
"""
polyinterface has a LOGGER that is created by default and logs to:
logs/debug.log
You can use LOGGER.info, LOGGER.warning, LOGGER.debug, LOGGER.error levels as needed.
"""
class Controller(polyinterface.Controller):
    def __init__(self, polyglot):
        super(Controller, self).__init__(polyglot)
        self.name = 'Tuya-Switch'
        self.poly.onConfig(self.process_config)
        self.ip = None
        self.uri = None
        self.item = None

    def start(self):
        # This grabs the server.json data and checks profile_version is up to date
        serverdata = self.poly.get_server_data()
        LOGGER.info('Started Tuya-Switch NodeServer {}'.format(serverdata['version']))
        self.check_params()
        #self.tuyaPlatform(self, self.uri, 'apiKey', 'apiSecret', 'Controller') #, 'uri', 'apiKey', 'apiSecret'
        self.poly.add_custom_config_docs("<b>And this is some custom config data</b>")
        # TODO: On start this should call self.discover() to fetch all the devices

    #class tuyaPlatform:
    #    def __init__(REGION, KEY, SECRET, uri):
    #        self.tuyaPlatform = Device()

    def shortPoll(self):
        self.discover() # TODO: This is wrong. We don't discovery on polling this should just query devices and update status

    def longPoll(self):
        self.discover() # TODO: This is wrong. We don't discovery on polling this should just query devices and update status

    def query(self,command=None):
        self.check_params()
        for node in self.nodes:
            # TODO: Needs to query each node self.nodes[node].query()
            self.nodes[node].reportDrivers()
    
    # TODO: What's the goal here? This looks like a start to a client library wrapper to handle authentication.
    # If so then it should be moved to a separate class to make it more portable. Although if this is trying to connect to the cloud API
    # you could use one that already exists: https://github.com/codetheweb/tuyapi
    def tuyaPlatform(self, apiRegion, apiKey, apiSecret, uri, token=None):
        request = "https://openapi.tuya%s.com/v1.0/%s" % (apiRegion,uri)
        now = int(time.time()*1000)
        if(token==None):
            payload = apiKey + str(now)
        else:
            payload = apiKey + token + str(now)

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
        response = requests.get(request, headers=headers)
        try:
            response_dict = json.loads(response.content.decode())
        except:
            try:
                response_dict = json.loads(response.content)
            except:
                LOGGER.debug("Failed to get valid JSON response")

        #return(response_dict)
        
    
    ## Wizard needs to run then each device found needs to be seperated as switch and light the added as each apropriate     
    #def wizard(self, command, color=True):
        # TODO: I'm assuming this isn't supposed to be part of the tuyaPlatform method. Indentation is wrong here.
        # This looks like a discovery method to me. But there is enough code here I would move it to a separate method
        # within the same class as the tuyaPlatform method above. Then I would just call that method from the discovery()
        # method in this controller to get the list of devices.
        config = {}
        config['apiKey'] = 'default_apiKey'  #'txejpdfda9iwmn5cg2es'
        config['apiSecret'] = 'default_apiSecret'   #'46d6072ffd724e0ba5ebeb5cc6b9dce9'
        config['apiRegion'] = 'us'
        config['apiDeviceID'] = 'default_apiDeviceId'  #'017743508caab5f0973e'
        needconfigs = True

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
        REGION = config['apiRegion'] # us, eu, cn, in
        LANG = 'en' # en or zh

        # Get Oauth Token from tuyaPlatform
        uri = 'token?grant_type=1'
        response_dict = tuyaPlatform(REGION, KEY, SECRET,uri)
        token = response_dict['result']['access_token']

        # Get UID from sample Device ID 
        uri = 'devices/%s' % DEVICEID
        response_dict = tuyaPlatform(REGION, KEY, SECRET, uri, token)
        uid = response_dict['result']['uid']

        # Use UID to get list of all Devices for User
        uri = 'users/%s/devices' % uid
        json_data = tuyaPlatform(REGION, KEY, SECRET, uri, token)
        response_dict = response_dict
    
        # Filter to only Name, ID and Key
        tuyadevices = []
        for i in json_data['result']:
            item = {}
            item['name'] = i['name'].strip()
            item['id'] = i['id']
            item['key'] = i['local_key']
            tuyadevices.append(item)

        #Display device list
        LOGGER.info("\n\n"  + "Device Listing\n" )
        output = json.dumps(tuyadevices, indent=4)  # sort_keys=True)
        LOGGER.info(output)

        # Save list to devices.json
        ##LOGGER.info(bold + "\n>> " + normal + "Saving list to " + DEVICEFILE)
        ##with open(DEVICEFILE, "w") as outfile:
        ##    outfile.write(output)
        ##LOGGER.info(dim + "    %d registered devices saved" % len(tuyadevices))
    
        # Scans network for devices and provide polling data
        if('Y'[0:1].lower() != 'n'):
            ##LOGGER.info(normal + "\nScanning local network for Tuya devices...")
            devices = tinytuya.deviceScan(False, 20)
            ##LOGGER.info("    %s%s local devices discovered%s" %
            ##      (len(devices)))
            ##LOGGER.info("")

            def getIP(d, gwid):
                for ip in d:
                    if (gwid == d[ip]['gwId']):
                        return (ip, d[ip]['version'])
                return (0, 0)

            polling = []
        # TODO: Confused why all this is needed. Are we polling just the cloud based API or local devices as well?
        # Local devices seem to be polled above in the tinytuya.deviceScan call but I'm not devices used down here
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
                LOGGER.info("    %s[%s] - %s%s - %sError: No IP found%s" %
                    (name, ip, name))
            else:
                try:
                    d = tinytuya.OutletDevice(i['id'], ip, i['key'])
                    if ver == "3.3":
                        d.set_version(3.3)
                    data = d.status()
                    if 'dps' in data:
                        item['devId'] = data
                        #state = alertdim + "Off" 
                        try:
                            ### if '20' in data['dps'] or '20' in data['devId']: for Light Nodes and 
                            ### if '1' in data['dps'] or '1' in data['devId']: for Switch Nodes
                            ### if '1' in data['dps'] or '20' in data['dps'] or '20' in data['devId']: for all Nodes Lights & Switches
                            if '1' in data['dps'] or '20' in data['devId'] or '1' in data['dps']:  
                                
                                #state = "On" 
                                #LOGGER.info("    %s[%s] - %s%s - %s - DPS: %r" %
                                #    (name, ip, state, data['dps'])
                                LOGGER.info("\nEACH TREATLIFE SWITCH TO NODE WITH ADDNODE FROM HERE!!!") ####### addNode Here?????
                                LOGGER.info("%-35.35s %-24s %-16s %-17s %-5s" % (
                                    item["name"],
                                    item["id"],
                                    item["ip"],
                                    item["key"],
                                    item["ver"]))
                                
                            else:
                                #LOGGER.info("    %s[%s] - %s%s - DPS: %r" %
                                #    (name, ip, data['dps']))
                                pass
                        except:
                            #LOGGER.info("    %s[%s] - %s%s - %sNo Response" %
                            #      (subbold, name, dim, ip, alertdim))
                            pass
                    else:
                        #LOGGER.info("    %s[%s] - %s%s - %sNo Response" %
                        #      (subbold, name, dim, ip, alertdim))
                        pass
                except:
                    pass
                    #LOGGER.info("    %s[%s] - %s%s - %sNo Response" %
                    #      (subbold, name, dim, ip, alertdim))
            polling.append(item)
        # for loop
    
        # Save polling data snapsot
        current = {'timestamp' : time.time(), 'devices' : polling}
        output = json.dumps(current, indent=4) 
        SWITCHID = i['id']
        SWITCHIP = item["ip"] 
        SWITCHKEY = item["key"] 
        LOGGER.info("Currently Passed Name:", 'item'["name"])
        LOGGER.info('SWITCHID') # Device Name
        #LOGGER.info(SWITCHIP) # Device IP
        #LOGGER.info(SWITCHKEY)
        LOGGER.info("TEST1 ID" + 'item'["id"]) # Device ID
        LOGGER.info("TEST1 KEY" + 'item'["key"]) # Device Key
########################## Need to send out  DEVICEID, DEVICEIP, DEVICEKEY for each node type Switch or Light found              
##### LOOP here and addNode,  add nodes as lights and switches?????????

    def discover(self,*args, **kwargs):    
        # TODO: This needs a list of devices and needs to loop through and add the appropriate nodes as required.
        # Anytime you call addNode you need to make sure you use a unique device_ID.
        # Each node needs something that makes it unique. In these I'm betting you can just use the Tuya device ID itself as it's probably already unique.
        # e.g., self.addNode(SwitchNode1(self, self.address, device.id, device.name))
        # TODO: It's up to you if you want to continue to use the controller as the parent grouping. I normally try to avoid
        # tying everything to the controller as the parent. If you want it to be standalone use the same device.id in place of self.address.
        # TODO: What is the difference between these classes? The names don't really tell me anything about what device it actually is.
        if "id" is not None:
            self.addNode(SwitchNodes1(self, self.address, 'tuyaswitch1', 'TreatLife-1')) # TODO: need to send DEVICEID, DEVICEIP, DEVICEKEY
        if "id" is not None: 
            self.addNode(SwitchNodes2(self, self.address, 'tuyaswitch2', 'TreatLife-2'))
        if "id" is not None: 
            self.addNode(LightNodes1(self, self.address, 'tuyalight1', 'TreatLifeLamp-1'))
        if "id" is not None: 
            self.addNode(LightNodes2(self, self.address, 'tuyalight2', 'TreatLifeLamp-2'))    
        if "id" is not None:
            self.addNode(SwitchNodes3(self, self.address, 'tuyaswitch3', 'TreatLife-3'))
                                    #item["name"],
                                    #item["id"],
                                    #item["ip"],
                                    #item["key"],
                                    #item["ver"])) 

    def delete(self):
        LOGGER.info('Removing Tuya Switch.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    # TODO: Is this needed? If not remove it.
    def process_config(self, config):
        # this seems to get called twice for every change, why?
        # What does config represent?
        LOGGER.info("process_config: Enter config={}".format(config));
        LOGGER.info("process_config: Exit");

    # TODO: Is this really needed? I know it's in the template but it feels like a duplicate of ST. Need to do some reading...
    def heartbeat(self,init=False):
        LOGGER.debug('heartbeat: init={}'.format(init))
        if init is not False:
            self.hb = init
        LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def set_module_logs(self,level):
        logging.getLogger('urllib3').setLevel(level)

    def set_debug_level(self,level):
        LOGGER.debug('set_debug_level: {}'.format(level))
        if level is None:
            level = 30
        level = int(level)
        if level == 0:
            level = 30
        LOGGER.info('set_debug_level: Set GV1 to {}'.format(level))
        self.setDriver('GV1', level)
        # 0=All 10=Debug are the same because 0 (NOTSET) doesn't show everything.
        if level <= 10:
            LOGGER.setLevel(logging.DEBUG)
        elif level == 20:
            LOGGER.setLevel(logging.INFO)
        elif level == 30:
            LOGGER.setLevel(logging.WARNING)
        elif level == 40:
            LOGGER.setLevel(logging.ERROR)
        elif level == 50:
            LOGGER.setLevel(logging.CRITICAL)
        else:
            LOGGER.debug("set_debug_level: Unknown level {}".format(level))
        # this is the best way to control logging for modules, so you can
        # still see warnings and errors
        #if level < 10:
        #    self.set_module_logs(logging.DEBUG)
        #else:
        #    # Just warnigns for the modules unless in module debug mode
        #    self.set_module_logs(logging.WARNING)
        # Or you can do this and you will never see mention of module logging
        if level < 10:
            LOG_HANDLER.set_basic_config(True,logging.DEBUG)
        else:
            # This is the polyinterface default
            LOG_HANDLER.set_basic_config(True,logging.WARNING)

    def check_params(self):
        """
        This is an example if using custom Params for user and password and an example with a Dictionary
        """
        self.removeNoticesAll()
        #self.addNotice('Hey there, my IP is {}'.format(self.poly.network_interface['addr']),'hello')
        #self.addNotice('Hello Friends! (without key)')
        default_apiKey = 'apiKey'
        default_apiSecret = 'apiSecert'
        default_apiDeviceId = 'apiDeviceId'
        default_apiRegion = "us"
        LANG = "en"


        # TODO: All variables need to be defined under __init__
        if 'apiKey' in self.polyConfig['customParams']:
            self.key = self.polyConfig['customParams']['apiKey']
        else:
            self.key = default_apiKey
            LOGGER.error('check_params: apiKey is not defined in customParams, please add it.  Using {}'.format(self.key))
            st = False

        if 'apiSecert' in self.polyConfig['customParams']:
            self.secert = self.polyConfig['customParams']['apiSecert']
        else:
            self.secert = default_apiSecret
            LOGGER.error('check_params: apiSecert is not defined in customParams, please add it.  Using {}'.format(self.secert))
            st = False

        if 'apiDeviceId' in self.polyConfig['customParams']:
            self.devid = self.polyConfig['customParams']['apiDeviceId']
        else:
            self.devid = default_apiDeviceId
            LOGGER.error('check_params: apiDeviceId is not defined in customParams, please add it.  Using {}'.format(self.devid))
            st = False    
        
        
        # Make sure they are in the params
        #'some_example': '{ "type": "TheType", "host": "host_or_IP", "port": "port_number" }'
        self.addCustomParam({'apiDeviceId': self.devid, 'apiSecert': self.secert, 'apiKey': self.key, })

        # Add a notice if they need to change the user/password from the default.
        #if self.key == default_apiKey or self.secert == default_apiSecret or self.devid == default_apiDeviceId:
            # This doesn't pass a key to test the old way.
            #self.addNotice('Please set proper apiKey and apiSecert in configuration page, and restart this nodeserver')
        # This one passes a key to test the new way.
        #self.addNotice('This is a test','test')

    
    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.poly.config['notices']))
        # Remove all existing notices
        self.removeNoticesAll()

    def update_profile(self,command):
        LOGGER.info('update_profile:')
        st = self.poly.installprofile()
        return st

    def cmd_set_debug_mode(self,command):
        val = int(command.get('value'))
        LOGGER.debug("cmd_set_debug_mode: {}".format(val))
        self.set_debug_level(val)

    """
    Optional.
    Since the controller is the parent node in ISY, it will actual show up as a node.
    So it needs to know the drivers and what id it will use. The drivers are
    the defaults in the parent Class, so you don't need them unless you want to add to
    them. The ST and GV1 variables are for reporting status through Polyglot to ISY,
    DO NOT remove them. UOM 2 is boolean.
    The id must match the nodeDef id="controller"
    In the nodedefs.xml
    """
    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
        'REMOVE_NOTICES_ALL': remove_notices_all,
        'SET_DM': cmd_set_debug_mode,

        
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV1', 'value': 10, 'uom': 25},

    ]

# TODO: Each of these classes really should be moved to it's own file. The addition of them all in here makes this file long and hard to read.
################################################################### NEED TWO PORGRAMS ONE FOR SWITCH ONE FOR LED LIGHTS #########################################################################
####### Need to be able to add nodes automatacally incrementing up their Class id's????   
####### Switch Node Manually input ID, IP & KEY as DEVICEID, DEVICEIP, DEVICEKEY This Needs to be passed from Controller to each node added, Switch or Light???? 
####### Now this is ugly but the only way i could get it to cycle Nodes
####### If i edit it to pass i get cipher errors and am not used to outside security
#       #DEVICEID = "017743508caab5f0973e"
#       #DEVICEIP = "192.168.1.147"
#       #DEVICEKEY = "e779c96c964f71b2"
# TODO: Singular: SwitchNode1 as this class doesn't represent a set of switch nodes but one individual one.
class SwitchNodes1(polyinterface.Node):
    def __init__(self, controller, primary, address, name): #, ip, id1, key1 key, ip, id
        super(SwitchNodes1, self).__init__(controller, primary, address, name)
        # TODO: Need a variable for the client library (if required for auth) being used to query this device
        # TODO: Should be class level variables self.name
        DEVICEID = "017743508caab5f0973e" # TODO: There should be no defaults here. These need to be set from the parameters in __init__
        DEVICEIP = "192.168.1.145"
        DEVICEKEY = "e779c96c964f71b2"
        DEVICEVERS = "us"
        #self.SWITCHID = SWITCHID
        #LOGGER.info(SWITCHID)
        #LOGGER.info("IP Address?" + 'IP')
        self.setDriver('ST', 1)
################# Need to Add actual Status from Devices
################# Need to figure out Status of Device to Driver for actual Status of Devices! #################
        # __init__:_decode_payload: decoded results='{"devId":"017743508caab5f385a7","dps":{"1":true},"t":1623487883}'
        #  __init__:set_status: set_status received data={'devId': '017743508caab5f385a7', 'dps': {'1': True}, 't': 1623487883}
        #LOGGER.info("\nREADING TEST: Response %r" % data)   
    def setSwOn(self, command):        
        # TODO: Again use class level variables
        DEVICEID = "017743508caab5f0973e" #"DEVICEID"
        DEVICEIP = "192.168.1.145" #"DEVICEIP"
        DEVICEKEY =  "e779c96c964f71b2" #"DEVICEKEY"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        # TODO: Why? In a deployed node server we'd never get these from the environment. The values for an instance of this
        # class would always come from discovery.
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        # self.nodes[input[key]['address']].runCmd(input[key])
        d = tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)#('DEVICEID'), ('DEVICEIP'), ('DEVICEKEY')
        d.set_version(3.3)
        LOGGER.info('    Turn Switch 1 On')
        #d.generate_payload(tinytuya.CONTROL, {'1': False, '2': 50})
        d.turn_on()
        self.setDriver('GV2', 1)

        # payload2=d.generate_payload(tinytuya.CONTROL, {'1': False, '2': 50})
        # payload1=d.generate_payload(tinytuya.CONTROL, {'1': True, '2': 50})

    def setSwOff(self, command):
        #TODO: See above
        DEVICEID = "017743508caab5f0973e"
        DEVICEIP = "192.168.1.145"
        DEVICEKEY = "e779c96c964f71b2"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        LOGGER.info('    Turn Switch 1 Off')
        d.turn_off()

        # TODO: Setting the driver is one way to update the ISY but after a state change I tend to like to query to device
        # instead. It ensures that the state you report isn't different from what actually happened.
        self.setDriver('GV2', 0)
        ############ Need to figure out Status of Device to Driver for actual Status of Devices! #################
        # __init__:_decode_payload: decoded results='{"devId":"017743508caab5f385a7","dps":{"1":true},"t":1623487883}'
        #  __init__:set_status: set_status received data={'devId': '017743508caab5f385a7', 'dps': {'1': True}, 't': 1623487883}
        #LOGGER.info("\nREADING TEST: Response %r" % data)


    def query(self,command=None):
        # TODO: This needs to actually query the device and get the current state of it.
        # It should then set the driver property
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1,2,3,4]
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV2', 'value': 1, 'uom': 2},

    ]
    
    id = 'tuyaswitch1'
    
    commands = {
                    'SWTON': setSwOn,
                    'SWTOF': setSwOff,
                    'QUERY': query,
    }

# TODO: Separate file. See the above SwitchNodes1 for additional comments.
####### Switch Node Manual ID, IP & KEY input to cycle 
class SwitchNodes2(polyinterface.Node):
    def __init__(self, controller, primary, address, name): #, ip, id1, key1 key, ip, id
        super(SwitchNodes2, self).__init__(controller, primary, address, name)
        
    def setSwOn(self, command):
        DEVICEID = "017743508caab5f385a7"
        DEVICEIP =  "192.168.1.155"
        DEVICEKEY = "7b8f2415ac96dfea"
        DEVICEVERS = "us"
        d=tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        # Check for environmental variables and always use those if available
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)
        

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        
        LOGGER.info('    Turn Switch 2 On')
        d.turn_on()
        self.setDriver('GV2', 1)
                
    def setSwOff(self, command):
        DEVICEID = "017743508caab5f385a7"
        DEVICEIP = "192.168.1.155"
        DEVICEKEY = "7b8f2415ac96dfea"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        LOGGER.info('    Turn Switch 2 Off')
        d.turn_off()
        #LOGGER.info('\nCurrent Status of', ['received data'], 'Light: %r' % 'dps')
        self.setDriver('GV2', 0)

    
    def query(self,command=None):
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1,2,3,4]
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV2', 'value': 0, 'uom': 2},

    ]
    
    id = 'tuyaswitch2'
    
    commands = {
                    'SWTON': setSwOn,
                    'SWTOF': setSwOff,
                    'QUERY': query,
    }

class SwitchNodes3(polyinterface.Node):
    def __init__(self, controller, primary, address, name): #, ip, id1, key1 key, ip, id
        super(SwitchNodes3, self).__init__(controller, primary, address, name)
        
    def setSwOn(self, command):
        DEVICEID = "017743508caab5f385a7"
        DEVICEIP =  "192.168.1.155"
        DEVICEKEY = "7b8f2415ac96dfea"
        DEVICEVERS = "us"
        d=tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        # Check for environmental variables and always use those if available
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)
        

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        
        LOGGER.info('    Turn Switch 2 On')
        d.turn_on()
        self.setDriver('GV2', 1)
                
    def setSwOff(self, command):
        DEVICEID = "017743508caab5f385a7"
        DEVICEIP = "192.168.1.155"
        DEVICEKEY = "7b8f2415ac96dfea"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.OutletDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        LOGGER.info('    Turn Switch 2 Off')
        d.turn_off()
        #LOGGER.info('\nCurrent Status of', ['received data'], 'Light: %r' % 'dps')
        self.setDriver('GV2', 0)

    
    def query(self,command=None):
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1,2,3,4]
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV2', 'value': 0, 'uom': 2},

    ]
    
    id = 'tuyaswitch2'
    
    commands = {
                    'SWTON': setSwOn,
                    'SWTOF': setSwOff,
                    'QUERY': query,
    }    

####### Light Node Manual ID, IP & KEY input to cycle
class LightNodes1(polyinterface.Node):
    def __init__(self, controller, primary, address, name): #, ip, id1, key1 key, ip, id
        super(LightNodes1, self).__init__(controller, primary, address, name)
        #self.ip = ip
        #self.id = id
        #self.key = key
        #self.data = data
        #LOGGER.info(ip)
    def setSwOn(self, command):
        DEVICEID = "ebfc16d57ed374932cjqfk"   
        DEVICEIP = "192.168.1.147"    
        DEVICEKEY = "805217605357161b"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Lamp Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        LOGGER.info('    Turn Lamp 1 On')
        d.turn_on()
        self.setDriver('GV2', 1)
                
    def setSwOff(self, command):
        DEVICEID = "ebfc16d57ed374932cjqfk"   
        DEVICEIP = "192.168.1.147"    
        DEVICEKEY = "805217605357161b"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Lamp Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        LOGGER.info('    Turn Lamp 1 Off')
        d.turn_off()
        self.setDriver('GV2', 0)

    def setclrflip(self, command):
        DEVICEID = "ebfc16d57ed374932cjqfk"   
        DEVICEIP = "192.168.1.147"    
        DEVICEKEY = "805217605357161b"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
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
        
        # Flip through colors of rainbow - set_colour(r, g, b):
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
        d.turn_off()
        self.setDriver('GV2', 0)
        time.sleep(1)
        LOGGER.info('\nDone')

    # Set Color
    def colorOn(self, command):
        DEVICEID = "ebfc16d57ed374932cjqfk"   
        DEVICEIP = "192.168.1.147"    
        DEVICEKEY = "805217605357161b"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        self.colorOn = int(command.get('value'))
        self.setDriver('GV5', self.colorOn)
        if self.colorOn == 0:
            d.set_colour(255,0,0)
            LOGGER.info('Red')
        elif self.colorOn == 1:
            d.set_colour(255,127,0)
            LOGGER.info('Orange')
        elif self.colorOn == 2:
            d.set_colour(255,200,0)
            LOGGER.info('Yellow')
        elif self.colorOn == 3:
            d.set_colour(0,255,0)
            LOGGER.info('Green')
        elif self.colorOn == 4:
            d.set_colour(0,0,255)
            LOGGER.info('Blue')
        elif self.colorOn == 5:
            d.set_colour(46,43,95)
            LOGGER.info('Indigo')
        elif self.colorOn == 6:
            d.set_colour(139,0,255)
            LOGGER.info('Violet')
        elif self.colorOn == 7:
            d.set_colour(255,255,255)
            LOGGER.info('White')                

    # Set Modes
    def modeOn(self, command):
        DEVICEID = "ebfc16d57ed374932cjqfk"   
        DEVICEIP = "192.168.1.147"    
        DEVICEKEY = "805217605357161b"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
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
            d.set_mode('white')
            LOGGER.info('White')
            

    # Led Level
    def setDim(self, command):
        DEVICEID = "ebfc16d57ed374932cjqfk"   
        DEVICEIP = "192.168.1.147"    
        DEVICEKEY = "805217605357161b"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
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

    def query(self,command=None):
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1,2,3,4]
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV2', 'value': 0, 'uom': 2},
            {'driver': 'GV3', 'value': 1, 'uom': 51},
            {'driver': 'GV4', 'value': 1, 'uom': 25},
            {'driver': 'GV5', 'value': 1, 'uom': 25},
            {'driver': 'GV6', 'value': 1, 'uom': 25},
            {'driver': 'GV7', 'value': 1, 'uom': 25},
            {'driver': 'GV8', 'value': 1, 'uom': 25},                  
    ]
    
    id = 'tuyalight1'
    
    commands = {
                    'LGTON': setSwOn,
                    'LGTOF': setSwOff,
                    'LGTCFLIP':setclrflip,
                    'COLOR': colorOn,
                    'MODE': modeOn,
                    'STLVL': setDim,
                    'QUERY': query,
    }
####### Light Node Manual ID, IP & KEY input to cycle
class LightNodes2(polyinterface.Node):
    def __init__(self, controller, primary, address, name): #, ip, id1, key1 key, ip, id
        super(LightNodes2, self).__init__(controller, primary, address, name)
        #self.ip = ip
        #self.id = id
        #self.key = key
        #self.data = data
        #LOGGER.info(ip)

    def setSwOn(self, command):
        DEVICEID = "ebfd4f4263bb769d99zjkq"   
        DEVICEIP = "192.168.1.146"    
        DEVICEKEY = "ec0b2b581a246eab"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Lamp Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        LOGGER.info('    Turn Lamp 1 On')
        d.turn_on()
        self.setDriver('GV2', 1)
                
    def setSwOff(self, command):
        DEVICEID = "ebfd4f4263bb769d99zjkq"   
        DEVICEIP = "192.168.1.146"    
        DEVICEKEY = "ec0b2b581a246eab"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Lamp Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        LOGGER.info('    Turn Lamp 1 Off')
        d.turn_off()
        self.setDriver('GV2', 0)

    def setclrflip(self, command):
        DEVICEID = "ebfd4f4263bb769d99zjkq"   
        DEVICEIP = "192.168.1.146"    
        DEVICEKEY = "ec0b2b581a246eab"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
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
        
        # Flip through colors of rainbow - set_colour(r, g, b):
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
        time.sleep(1)
        LOGGER.info('\nDone')

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
        d.turn_off()
        self.setDriver('GV2', 0)
        time.sleep(1)
        LOGGER.info('\nDone')

    # Set Color
    def colorOn(self, command):
        DEVICEID = "ebfd4f4263bb769d99zjkq"   
        DEVICEIP = "192.168.1.146"    
        DEVICEKEY = "ec0b2b581a246eab"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
        d=tinytuya.BulbDevice(DEVICEID, DEVICEIP, DEVICEKEY)
        d.set_version(3.3)
        d.set_socketPersistent(True)
        self.colorOn = int(command.get('value'))
        self.setDriver('GV5', self.colorOn)
        if self.colorOn == 0:
            d.set_colour(255,0,0)
            LOGGER.info('Red')
        elif self.colorOn == 1:
            d.set_colour(255,127,0)
            LOGGER.info('Orange')
        elif self.colorOn == 2:
            d.set_colour(255,200,0)
            LOGGER.info('Yellow')
        elif self.colorOn == 3:
            d.set_colour(0,255,0)
            LOGGER.info('Green')
        elif self.colorOn == 4:
            d.set_colour(0,0,255)
            LOGGER.info('Blue')
        elif self.colorOn == 5:
            d.set_colour(46,43,95)
            LOGGER.info('indigo')
        elif self.colorOn == 6:
            d.set_colour(139,0,255)
            LOGGER.info('Violet')
        elif self.colorOn == 7:
            d.set_colour(255,255,255)
            LOGGER.info('White')       

    # Set Modes
    def modeOn(self, command):
        DEVICEID = "ebfd4f4263bb769d99zjkq"   
        DEVICEIP = "192.168.1.146"    
        DEVICEKEY = "ec0b2b581a246eab"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
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
            d.set_mode('white')
            LOGGER.info('White')

    # Led Level
    def setDim(self, command):
        DEVICEID = "ebfd4f4263bb769d99zjkq"   
        DEVICEIP = "192.168.1.146"    
        DEVICEKEY = "ec0b2b581a246eab"
        DEVICEVERS = "us"
        # Check for environmental variables and always use those if available
        DDEVICEID = os.getenv("DEVICEID", DEVICEID)
        DEVICEIP = os.getenv("DEVICEIP", DEVICEIP)
        DEVICEKEY = os.getenv("DEVICEKEY", DEVICEKEY)
        DEVICEVERS = os.getenv("DEVICEVERS", DEVICEVERS)

        LOGGER.info("TreatLife - Smart Switch Test [%s]\n" % tinytuya.__version__)
        LOGGER.info('TESTING: Device %s at %s with key %s version %s' %
                    (DEVICEID, DEVICEIP, DEVICEKEY, DEVICEVERS))

        LOGGER.info('TESTING: Device %s' %
                    (DEVICEIP))
        
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
            d.set_brightness_percentage(percent)            
            self.setDriver('GV3', percent)
    
    def query(self,command=None):
        self.reportDrivers()

    "Hints See: https://github.com/UniversalDevicesInc/hints"
    hint = [1,2,3,4]
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV2', 'value': 0, 'uom': 2},
            {'driver': 'GV3', 'value': 1, 'uom': 51},
            {'driver': 'GV4', 'value': 1, 'uom': 25},
            {'driver': 'GV5', 'value': 1, 'uom': 25},
            {'driver': 'GV6', 'value': 1, 'uom': 25},
            {'driver': 'GV7', 'value': 1, 'uom': 25},
            {'driver': 'GV8', 'value': 1, 'uom': 25},                  
    ]
    
    id = 'tuyalight2'
    
    commands = {
                    'LGTON': setSwOn,
                    'LGTOF': setSwOff,
                    'LGTCFLIP':setclrflip,
                    'COLOR': colorOn,
                    'MODE': modeOn,
                    'STLVL': setDim,
                    'QUERY': query,
    }

if __name__ == "__main__":
    try:
        polyglot = polyinterface.Interface('TuyaSwitch')
        polyglot.start()
        control = Controller(polyglot)
        control.runForever()
        ""
    except (KeyboardInterrupt, SystemExit):
        polyglot.stop()
        sys.exit(0)
        """
        Catch SIGTERM or Control-C and exit cleanly.
        """
