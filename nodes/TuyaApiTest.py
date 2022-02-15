import logging
from tuya_connector import TuyaOpenAPI, TUYA_LOGGER

ACCESS_ID = "txejpdfda9iwmn5cg2es"
ACCESS_KEY = "46d6072ffd724e0ba5ebeb5cc6b9dce9"
API_ENDPOINT = "https://openapi.tuyaus.com"



# Enable debug log
TUYA_LOGGER.setLevel(logging.DEBUG)

# Init OpenAPI and connect
openapi = TuyaOpenAPI(API_ENDPOINT, ACCESS_ID, ACCESS_KEY)
openapi.connect()

# Set up device_id
DEVICE_ID1 ="ebfc16d57ed374932cjqfk"

# Call APIs from Tuya
# Get the device information
#response = openapi.get("/v1.0/iot-03/devices/{}".format(DEVICE_ID1))

# Get the instruction set of the device
#response = openapi.get("/v1.0/iot-03/devices/{}/functions".format(DEVICE_ID1))

# Send commands
#commands1 = {'commands': [{'code': 'switch_led', 'value': False}]}
#commands1 = {'commands': [{'code': 'bright_value_v2', 'value': 10}]} # Brightness 10-1000
#commands1 = {'commands': [{'code': 'temp_value_v2', 'value': 255}]} # Temp 0-1000
#commands1 = {'commands': [{'code': 'work_mode', 'value': 'colour'}]} # MODE "{\"range\":[\"white\",\"colour\",\"scene\",\"music\"]}"
commands1 = {'commands': [{'code': 'colour_data_v2', 'value': "{\"h\":0,\"s\":0,\"v\":1000}"}]} # color




openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID1), commands1)

# Get the status of a single device
response = openapi.get("/v1.0/iot-03/devices/{}/status".format(DEVICE_ID1))

#DEVICE_ID2 = "017743508caab5f0973e" #"017743508caab5f385a7" "017743508caab5f0973e"

# Call APIs from Tuya
# Get the device information
#response = openapi.get("/v1.0/iot-03/devices/{}".format(DEVICE_ID2))

# Get the instruction set of the device
#response = openapi.get("/v1.0/iot-03/devices/{}/functions".format(DEVICE_ID2))

# Send commands
#commands2 = {'commands': [{'code': 'switch_1', 'value': False}]}


#openapi.post('/v1.0/iot-03/devices/{}/commands'.format(DEVICE_ID2), commands2)

# Get the status of a single device
#response = openapi.get("/v1.0/iot-03/devices/{}/status".format(DEVICE_ID2))