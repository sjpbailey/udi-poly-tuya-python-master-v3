# TinyTuya Setup Wizard
# -*- coding: utf-8 -*-
"""
TinyTuya Setup Wizard Tuya based WiFi smart devices

Author: Jason A. Cox
For more information see https://github.com/jasonacox/tinytuya

Description
    Setup Wizard will prompt the user for Tuya IoT Developer credentials and will gather all
    registered Device IDs and their Local KEYs.  It will save the credentials and the device
    data in the tinytuya.json and devices.json configuration files respectively. The Wizard
    will then optionally scan the local devices for status.

    HOW to set up your Tuya IoT Developer account: iot.tuya.com:
    https://github.com/jasonacox/tinytuya#get-the-tuya-device-local-key

Credits
* Tuya API Documentation
    https://developer.tuya.com/en/docs/iot/open-api/api-list/api?id=K989ru6gtvspg
* TuyaAPI https://github.com/codetheweb/tuyapi by codetheweb and blackrozes
    The TuyAPI/CLI wizard inspired and informed this python version.
"""
# Modules
from __future__ import print_function
import hmac
import hashlib
import ipaddress
import json
import socket
import time
import requests
from colorama import init
import tinytuya

# Optional libraries required for forced scanning
try:
    from getmac import get_mac_address
    SCANLIBS = True
except:
    # Disable force scanning
    SCANLIBS = False

# Backward compatability for python2
try:
    input = raw_input
except NameError:
    pass

# Colorama terminal color capability for all platforms
init()

# Configuration Files
DEVICEFILE = 'devices.json'  # tinytuya.DEVICEFILE
SNAPSHOTFILE = 'snapshot.json'  # tinytuya.SNAPSHOTFILE
CONFIGFILE = 'config.json'  # tinytuya.CONFIGFILE
RAWFILE = 'tuya-raw.json'  # tinytuya.RAWFILE

# Global Network Configs
#DEFAULT_NETWORK = tinytuya.DEFAULT_NETWORK
# TCPTIMEOUT = tinytuya.TCPTIMEOUT    # Seconds to wait for socket open for scanning
# TCPPORT = tinytuya.TCPPORT          # Tuya TCP Local Port

# Helper Functions


def getmyIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    r = s.getsockname()[0]
    s.close()
    return r


def wizard(color=True, retries=None, forcescan=False):
    """
    TinyTuya Setup Wizard Tuya based WiFi smart devices

    Parameter:
        color = True or False, print output in color [Default: True]
        retries = Number of retries to find IP address of Tuya Devices
        forcescan = True or False, force network scan for device IP addresses

    Description
        Setup Wizard will prompt user for Tuya IoT Developer credentials and will gather all of
        the Device IDs and their Local KEYs.  It will save the credentials and the device
        data in the tinytuya.json and devices.json configuration files respectively.

        HOW to set up your Tuya IoT Developer account: iot.tuya.com:
        https://github.com/jasonacox/tinytuya#get-the-tuya-device-local-key

    Credits
    * Tuya API Documentation
        https://developer.tuya.com/en/docs/iot/open-api/api-list/api?id=K989ru6gtvspg
    * TuyaAPI https://github.com/codetheweb/tuyapi by codetheweb and blackrozes
        The TuyAPI/CLI wizard inspired and informed this python version.
    """

    config = {}
    ip_list = {}
    config['apiKey'] = ''
    config['apiSecret'] = ''
    config['apiRegion'] = ''
    config['apiDeviceID'] = ''
    needconfigs = True
    try:
        # Load defaults
        with open(CONFIGFILE) as f:
            config = json.load(f)
    except:
        # First Time Setup
        pass

    # (bold,   normal,   alert,  ,
    # cyan, red, yellow) = tinytuya.termcolor(color)

    print('TinyTuya Setup Wizard' +
          ' [%s]' % (tinytuya.version))
    print('')

    if forcescan:
        if not SCANLIBS:
            print(
                '    ERROR: force network scanning requested but not available - disabled.\n'
                '           (Requires: pip install getmac)\n')
            forcescan = False
        else:
            print("    Option: " +
                  "Network force scanning requested.\n")

    if (config['apiKey'] != '' and config['apiSecret'] != '' and
            config['apiRegion'] != '' and config['apiDeviceID'] != ''):
        needconfigs = False
        print("    " + "Existing settings:" +
              "\n        API Key=%s \n        Secret=%s\n        DeviceID=%s\n        Region=%s" %
              (config['apiKey'], config['apiSecret'], config['apiDeviceID'],
               config['apiRegion']))
        print('')
        answer = input('    Use existing credentials ' +
                       '(Y/n): ')
        if answer[0:1].lower() == 'n':
            needconfigs = True

    if needconfigs:
        # Ask user for config settings
        print('')
        config['apiKey'] = input("    Enter " + "API Key" +
                                 " from tuya.com: ")
        config['apiSecret'] = input("    Enter " + "API Secret" +
                                    " from tuya.com: ")
        config['apiDeviceID'] = input(
            "    Enter " + "any Device ID" +
            " currently registered in Tuya App (used to pull full list): ")
        # TO DO - Determine apiRegion based on Device - for now, ask
        print("\n      " + "Region List" +
              "\n        cn\tChina Data Center" +
              "\n        us\tUS - Western America Data Center" +
              "\n        us-e\tUS - Eastern America Data Center" +
              "\n        eu\tCentral Europe Data Center" +
              "\n        eu-w\tWestern Europe Data Center" +
              "\n        in\tIndia Data Center\n")
        config['apiRegion'] = input("    Enter " + "Your Region" +
                                    " (Options: cn, us, us-e, eu, eu-w, or in): ")
        # Write Config
        json_object = json.dumps(config, indent=4)
        with open(CONFIGFILE, "w") as outfile:
            outfile.write(json_object)
        print("\n>> Configuration Data Saved to " + CONFIGFILE)
        print(json_object)

    KEY = config['apiKey']
    SECRET = config['apiSecret']
    DEVICEID = config['apiDeviceID']
    REGION = config['apiRegion']        # us, eu, cn, in

    cloud = tinytuya.Cloud(**config) 

    # on auth error getdevices() will implode
    if cloud.error:
        err = cloud.error['Payload'] if 'Payload' in cloud.error else 'Unknown Error'
        print('\n\n' + 'Error from Tuya server: ' + err)
        print('Check API Key and Secret')
        return

    # Get UID from sample Device ID
    json_data = cloud.getdevices(True)

    if 'result' not in json_data:
        err = json_data['Payload'] if 'Payload' in json_data else 'Unknown Error'
        print('\n\n' + 'Error from Tuya server: ' + err)
        print('Check DeviceID and Region')
        return

    if forcescan:
        # Force Scan - Get list of all local ip addresses
        try:
            # Fetch my IP address and assume /24 network
            ip = getmyIP()
            network = ipaddress.IPv4Interface(u''+ip+'/24').network
        except:
            network = DEFAULT_NETWORK
            ip = None
            print(
                'ERROR: Unable to get your IP address and network automatically.\n'
                '       (using %s)' % network)

        try:
            # Warn user of scan duration
            print("\n" +
                  "Scanning local network.  This may take a while...")
            print('\n    Running Scan...')
            # Loop through each host
            for addr in ipaddress.IPv4Network(network):
                # Fetch my IP address and assume /24 network
                print('\r      Host: ' + '%s ...' %
                      addr, end='')
                a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                a_socket.settimeout(TCPTIMEOUT)
                location = (str(addr), TCPPORT)
                result_of_check = a_socket.connect_ex(location)
                if result_of_check == 0:
                    # TODO: Verify Tuya Device
                    ip = "%s" % addr
                    mac = get_mac_address(ip=ip)
                    ip_list[mac] = ip
                    print(" Found Device [%s]" % mac)
                a_socket.close()

            print('\r      Done                           ' +
                  '\n\nDiscovered %d Tuya Devices\n' % len(ip_list))
        except:
            print('\n' + '    Error scanning network - Ignoring')
            forcescan = False

    # Filter to only Name, ID and Key, IP and mac-address
    tuyadevices = cloud.filter_devices(json_data['result'], ip_list)

    for dev in tuyadevices:
        if 'sub' in dev and dev['sub'] and 'key' in dev:
            found = False
            for parent in tuyadevices:
                # the local key seems to be the only way of identifying the parent device
                if 'key' in parent and 'id' in parent and dev['key'] == parent['key']:
                    found = parent
                    break
            if found:
                dev['parent'] = found['id']

    # Display device list
    print("\n\n" + "Device Listing\n")
    output = json.dumps(tuyadevices, indent=4)  # sort_keys=True)
    print(output)

    # Save list to devices.json
    print("\n>> " + "Saving list to " + DEVICEFILE)
    with open(DEVICEFILE, "w") as outfile:
        outfile.write(output)
    print("    %d registered devices saved" % len(tuyadevices))

    # Save raw TuyaPlatform data to tuya-raw.json
    print("\n>> " +
          "Saving raw TuyaPlatform response to " + RAWFILE)
    try:
        with open(RAWFILE, "w") as outfile:
            outfile.write(json.dumps(json_data, indent=4))
    except:
        print('\n\n' + 'Unable to save raw file')

    # Find out if we should poll all devices
    answer = input('\nPoll local devices? ' +
                   '(Y/n): ')
    if answer[0:1].lower() != 'n':
        # Set retries based on number of devices if undefined
        if retries is None:
            retries = len(tuyadevices)+10+tinytuya.MAXCOUNT

        # Scan network for devices and provide polling data
        print("\nScanning local network for Tuya devices (retry %d times)..." % retries)
        devices = tinytuya.deviceScan(False, retries)
        print("    %s%s local devices discovered%s" %
              (len(devices)))
        print("")

        def getIP(d, gwid):
            for ip in d:
                if 'gwId' in d[ip]:
                    if gwid == d[ip]['gwId']:
                        return (ip, d[ip]['version'])
            return (0, 0)

        polling = []
        print("Polling local devices...")
        for i in tuyadevices:
            item = {}
            name = i['name']
            (ip, ver) = getIP(devices, i['id'])
            item['name'] = name
            item['ip'] = ip
            item['ver'] = ver
            item['id'] = i['id']
            item['key'] = i['key']
            if ip == 0:
                print("    %s[%s] - %s%s - %sError: No IP found%s" %
                      (name,   ip))
            else:
                try:
                    d = tinytuya.OutletDevice(i['id'], ip, i['key'])
                    d.set_version(float(ver))
                    data = d.status()
                    if 'dps' in data:
                        item['dps'] = data
                        state = + "Off"
                        try:
                            if '1' in data['dps'] or '20' in data['dps']:
                                if '1' in data['dps']:
                                    if data['dps']['1'] is True:
                                        state = "On"
                                if '20' in data['dps']:
                                    if data['dps']['20'] is True:
                                        state = "On"
                                print("    %s[%s] - %s%s - %s - DPS: %r" %
                                      (name,   ip, state, data['dps']))
                            else:
                                print("    %s[%s] - %s%s - DPS: %r" %
                                      (name,   ip, data['dps']))
                        except:
                            print("    %s[%s] - %s%s - %sNo Response" %
                                  (name,   ip,))
                    else:
                        print("    %s[%s] - %s%s - %sNo Response" %
                              (name,   ip,))
                except:
                    print("    %s[%s] - %s%s - %sNo Response" %
                          (name,   ip,))
            polling.append(item)
        # for loop

        # Save polling data snapsot
        current = {'timestamp': time.time(), 'devices': polling}
        output = json.dumps(current, indent=4)
        print("\n>> " +
              "Saving device snapshot data to " + SNAPSHOTFILE)
        with open(SNAPSHOTFILE, "w") as outfile:
            outfile.write(output)

    print("\nDone.\n")
    return


if __name__ == '__main__':

    try:
        wizard()
    except KeyboardInterrupt:
        pass
