# Universal Devices Tuya Product NodeServer

* BETA! This will Probably NOT work on your network due to json usage by Tintuya Module!
It will probably need to be rebuilt into a cloud node server. If you have tuya devices files may need to be written

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

### Setup Wizard - Getting Local Keys

TinyTuya has a built-in setup Wizard that uses the Tuya IoT Cloud Platform to generate a JSON list (devices.json) of all your registered devices, including secret *Local_Key* and *Name* of your devices. Follow the steps below:

1. PAIR - Download the *Smart Life App* or *Tuya Smart App*, available for [iPhone](https://itunes.apple.com/us/app/smart-life-smart-living/id1115101477?mt=8) or [Android](https://play.google.com/store/apps/details?id=com.tuya.smartlife&hl=en). Pair all of your Tuya devices (this is important as you cannot access a device that has not been paired).

2. SCAN (Optional) - Run the TinyTuya scan to get a list of Tuya devices on your network. It will show device *Address*, *Device ID* and *Version* number (3.x):

    ```bash
    python -m tinytuya scan
    ```

    You may need to run python -m tinytuya wizard first and set your credentials for the above Bash to work.
  
    NOTE: You will need to use one of the displayed *Device IDs* for step 4.

3. TUYA ACCOUNT - Set up a Tuya Account (see [PDF Instructions](https://github.com/jasonacox/tinytuya/files/8145832/Tuya.IoT.API.Setup.pdf)):
    * *NOTE: Tuya often changes their portal and services. Please open an [issue](https://github.com/jasonacox/tinytuya/issues) with screenshots if we need to update these instructions.*
    * Create a Tuya Developer account on [iot.tuya.com](https://iot.tuya.com/). When it asks for the "Account Type", select "Skip this step..." (see [screenshot](https://user-images.githubusercontent.com/836718/213877860-34c39851-5671-4c9f-b4d5-251873f18c77.png)).  
    * Click on "Cloud" icon -> "Create Cloud Project"
      1. Remember the "Data Center" you select.  This will be used by TinyTuya Wizard ([screenshot](https://user-images.githubusercontent.com/836718/138598647-c9657e49-1a89-4ed6-8105-ceee95d9513f.png)).
      2. Skip the configuration wizard but remember the Authorization Key: *API ID* and *Secret* for below ([screenshot](https://user-images.githubusercontent.com/836718/138598788-f74d2fe8-57fa-439c-8003-18735a44e7e5.png)).
    * Click on "Cloud" icon -> Select your project -> **Devices** -> **Link Tuya App Account** ([see screenshot](https://user-images.githubusercontent.com/836718/155827671-44d5fce4-0119-4d0e-a224-ef3715fafc24.png))
    * Click **Add App Account** ([screenshot](https://user-images.githubusercontent.com/836718/155827671-44d5fce4-0119-4d0e-a224-ef3715fafc24.png)) and it will display a QR code. Scan the QR code with the *Smart Life app* on your Phone (see step 1 above) by going to the "Me" tab in the *Smart Life app* and clicking on the QR code button `[..]` in the upper right hand corner of the app. When you scan the QR code, it will link all of the devices registered in your *Smart Life app* into your Tuya IoT project.
    * **NO DEVICES?** If no devices show up after scanning the QR code, you will need to select a different data center and edit your project (or create a new one) until you see your paired devices from the *Smart Life App* show up. ([screenshot](https://user-images.githubusercontent.com/35581194/148679597-391adecb-a271-453b-90c0-c64cdfad42e4.png)). The data center may not be the most logical. As an example, some in the UK have reported needing to select "Central Europe" instead of "Western Europe".
    * **SERVICE API:** Under "Service API" ensure these APIs are listed: `IoT Core`, `Authorization` and `Smart Home Scene Linkage`. To be sure, click subscribe again on every service.  Very important: **disable popup blockers** otherwise subscribing won't work without providing any indication of a failure. Make sure you authorize your Project to use those APIs:
        * Click "Service API" tab
        * Click "**Go to Authorize**" button
        * Select the API Groups from the dropdown and click `Subscribe` ([screenshot](https://user-images.githubusercontent.com/38729644/128742724-9ed42673-7765-4e21-94c8-76022de8937a.png))

4. WIZARD - Run Setup Wizard:
    * Tuya has changed their data center regions. Make sure you are using the latest version of TinyTuya (v1.2.10 or newer).
    * From your Linux/Mac/Win PC run the TinyTuya Setup **Wizard** to fetch the *Local_Keys* for all of your registered devices:

      ```bash
      python -m tinytuya wizard   # use -nocolor for non-ANSI-color terminals
      ```

    * The **Wizard** will prompt you for the *API ID* key, API *Secret*, API *Region* (cn, us, us-e, eu, eu-w, or in) from your Tuya IoT project as set in Step 3 above.
        * To find those again, go to [iot.tuya.com](https://iot.tuya.com/), choose your project and click `Overview`
            * API Key: Access ID/Client ID
            * API Secret: Access Secret/Client Secret
    * It will also ask for a sample *Device ID*.  You can have the wizard scan for one (enter `scan`), use one from step 2 above or in the Device List on your Tuya IoT project.
    * The **Wizard** will poll the Tuya IoT Cloud Platform and print a JSON list of all your registered devices with the "name", "id" and "key" of your registered device(s). The "key"s in this list are the Devices' *Local_Key* you will use to access your device.
    * In addition to displaying the list of devices, **Wizard** will create a local file `devices.json` that TinyTuya will use to provide additional details for scan results from `tinytuya.deviceScan()` or when running `python -m tinytuya scan`. The wizard also creates a local file `tuya-raw.json` that contains the entire payload from Tuya Cloud.
    * The **Wizard** will ask if you want to poll all the devices. If you do, it will display the status of all devices on record and create a `snapshot.json` file with these results. Make sure your LAN and firewall permit UDP (6666, 6667 and 7000) and TCP (6668) traffic.

Notes:

* If you ever reset or re-pair your smart devices, the *Local_Key* will be reset and you will need to repeat the steps above.
* The TinyTuya *Wizard* was inspired by the TuyAPI CLI which is an alternative way to fetch the *Local_Keys*: `npm i @tuyapi/cli -g` and run `tuya-cli wizard`  

## Requirements-

1. Polyglot V3.
2. ISY firmware 5.3.x or later
3. tinytuya 1.12.7

### Release Notes

* 1.0.0 08/11/2021

* Initial version published to github
