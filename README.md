# Universal Devices Tuya Product NodeServer

## Currently for TreatLife Switches and LED Bulbs

## Description

This is based on the python module by Jason Cox it controls and monitors [Tuya](https://en.tuya.com/) compatible WiFi Smart Devices (Plugs, Switches, Lights, Window Covers, etc.) using the local area network (LAN).  This is a compatible replacement for the `pytuya` PyPi module.

[Tuya](https://en.tuya.com/) devices are designed to communicate with the TuyaCloud but most also expose a local area network API, allowing us to directly control the devices without using the cloud. This python module provides a socket based way to poll status and issue commands to these devices.

![TinyTuya Diagram](https://raw.githubusercontent.com/jasonacox/tinytuya/master/docs/TinyTuya-diagram.svg)

NOTE: This module requires the devices to have already been **activated** by Smart Life App (or similar).

## Tuya Device Preparation

Controlling and monitoring Tuya devices on your network requires the following:

* *Address* - The network address (IPv4) of the device e.g. 10.0.1.100
* *Device ID* - The unique identifier for the Tuya device
* *Version* - The Tuya protocol version used (3.1 or 3.3)
* *Local_Key* - The security key created to encrypt and decrypt communication. Devices running the latest protocol version 3.3 (e.g. Firmware 1.0.5 or above) will require a device *Local_Key* to read the status. Both 3.1 and 3.3 devices will require a device *Local_Key* to control the device.

### Network Scanner

TinyTuya has a built in network scanner that can be used to find Tuya Devices on your local network. It will show *Address*, *Device ID* and *Version* for each device.  

```bash
python -m tinytuya scan
```

### Setup Wizard

TinyTuya has a built in setup Wizard that uses the Tuya IoT Cloud Platform to generate a JSON list (devices.json) of all your registered devices. This includes the secret *Local_Key* as well as the *Name* of each device.

Follow the instructions below to get the *Local_Key*:

1. Download the "Smart Life" App, available for iPhone or Android. Pair all of your Tuya devices (this is important as you cannot access a device that has not been paired).  
    * <https://itunes.apple.com/us/app/smart-life-smart-living/id1115101477?mt=8>
    * <https://play.google.com/store/apps/details?id=com.tuya.smartlife&hl=en>

2. Run the TinyTuya scan to get a list of Tuya devices on your network along with their device *Address*, *Device ID* and *Version* number (3.1 or 3.3):

    ```bash
    python -m tinytuya scan
    ```

    **NOTE:** You will need to use one of the displayed *Device IDs* for step 4.

3. **Set up a Tuya Account**:
    * Create a Tuya Developer account on [iot.tuya.com](https://iot.tuya.com/) and log in.
    * Click on "Cloud" icon -> Create Cloud Project (Skip the configuration wizard) (remember the Authorization Key: *API ID* and *Secret* for below)
    * Click on "Cloud" icon -> Select your project -> Devices -> Add Device
    * Click `Add Device with IoT Device Management App` and it will display a QR code. Scan the QR code with the *Smart Life app* on your Phone (see step 1 above) by going to the "Me" tab in the *Smart Life app* and clicking on the QR code button [..] in the upper right hand corner of the app. When you scan the QR code, it will link all of the devices registered in your "Smart Life" app into your Tuya IoT project.
    * **IMPORTANT** Under "Service API" ensure the API groups are listed: `Smart Home Devices Management`, `Authorization` and `Smart Home Family Management` ([see screenshot here](https://user-images.githubusercontent.com/38729644/128742250-9b2a0c0e-4f5b-4886-8279-cd50bfeedcf8.png)) - Make sure you authorize your Project to use these 3 API groups:
        * Click "Service API" tab
        * Click "**Go to Authorize**" button
        * Select the API Groups from the dropdown and click `Subscribe` ([see screenshot here](https://user-images.githubusercontent.com/38729644/128742724-9ed42673-7765-4e21-94c8-76022de8937a.png))

4. **Run Setup Wizard**:
    * From your Linux/Mac/Win PC run the TinyTuya Setup **Wizard** to fetch the  *Local_Keys* for all of your registered devices:

      ```bash
      python -m tinytuya wizard   # use -nocolor for non-ANSI-color terminals
      ```

    * The **Wizard** will prompt you for the *API ID* key, API *Secret*, API *Region* (us, eu, cn or in) from your Tuya IoT project.
        * Go to [iot.tuya.com](https://iot.tuya.com/), choose your project and click `Overview`
            * API Key: Access ID/Client ID
            * API Secret: Access Secret/Client Secret
    * It will also ask for a sample *Device ID*.  Use one from step 2 above or found in the Device List on your Tuya IoT project.
    * The **Wizard** will poll the Tuya IoT Cloud Platform and print a JSON list of all your registered devices with the "name", "id" and "key" of your registered device(s). The "key"s in this list are the Devices' *Local_Key* you will use to access your device.
    * In addition to displaying the list of devices, **Wizard** will create a local file `devices.json`.  TinyTuya will use this file to provide additional details to scan results from `tinytuya.deviceScan()` or when running `python -m tinytuya` to scan your local network.  
    * The **Wizard** will ask if you want to poll all the devices. If you do, it will display the status of all devices on records and create a `snapshot.json` file with the results.

Notes:

* If you ever reset or re-pair your smart devices, the *Local_Key* will be reset and you will need to repeat the steps above.
* The TinyTuya *Wizard* was inspired by the TuyAPI CLI which is an alternative way to fetch the *Local_Keys*: `npm i @tuyapi/cli -g` and run `tuya-cli wizard`  
* For a helpful video walk-through of getting the *Local_Keys* you can also watch this great _Tech With Eddie_ YouTube tutorial: <https://youtu.be/oq0JL_wicKg>.

## Requirements

1. Polyglot V3.
2. ISY firmware 5.3.x or later

### Release Notes

* 1.0.0 08/11/2021

* Initial version published to github
