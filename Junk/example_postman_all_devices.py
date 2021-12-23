"""import requests

#curl -H "client_id:e7r9rp3fab1jtlja761b" -H "sign:14ADCB6FEDC822CC2CBA8537770453E90683B9E9C5B96C851AEB78C4F078C739" -H "sign_method:HMAC-SHA256" -H "t:1614851428586" -H "lang:en" "https://openapi.tuyacn.com/v1.0/token? grant_type=1"
# Token URL: url = "https://openapi.tuyaus.com/v1.0/token?grant_type=1"
# Refresh Token: URL url = "https://openapi.tuyaus.com/v1.0/token/ea5efab1617ce53cc450fe852cd9f051"
url = "https://openapi.tuyaus.com/v1.0/users/az1610958067414WkfOO/devices"

payload={}
headers = {
  'client_id': 'txejpdfda9iwmn5cg2es',
  'access_token': 'b501eeac284101bf055f85a75f9ce0c7',
  'sign': '6920FD1AAE7E072CBBAE41BA0E09DD2B71D6E837E5FE97479C81121F95AB0D58',
  't': '1632982191681',
  'sign_method': 'HMAC-SHA256'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)





import requests

url = "https://openapi.tuyaus.com/v1.0/token?grant_type=1"

payload={}
headers = {
  'client_id': 'txejpdfda9iwmn5cg2es',
  'sign': '3D0C5E020A33B791E2E2955FD654FBA91B4D0568601EEF3CE9247E5F945527F0',
  't': '1633044762056',
  'sign_method': 'HMAC-SHA256'
}

response_token = requests.request("GET", url, headers=headers, data=payload)

print(response_token.text)"""



#import requests

#client_id = 123
#client_secret = 123
#refresh_token= open('C:\Users\james.weston1\Desktop\access_token.json')

#url = "https://eu-apigw.central.arubanetworks.com/oauth2/token"

#qparams = {"client_id": "$CLIENT_ID", "client_secret": "$CLIENT_SECRET", "grant_type":"refresh_token", "refresh_token":"$REFRESH_TOKEN"}

#response = requests.request("POST", url, params=qparams)

#print(response.text.encode('utf8'))"""

"""import requests
import json

client_id = 'txejpdfda9iwmn5cg2es'
client_secret = '46d6072ffd724e0ba5ebeb5cc6b9dce9'
url = "https://openapi.tuyaus.com/v1.0/users/az1610958067414WkfOO/devices"

with open(response) as f:
    # Parse the file contents as json
    access_data = json.load(f)
    # Get the refresh token from the resulting dict
    refresh_token = access_data['refresh_token']

qparams = {
    "grant_type":"refresh_token",
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token
}

response = requests.request("POST", url, params=qparams)

print(response.text.encode('utf8'))"""

import requests

url = "https://openapi.tuyaus.com/v1.0/users/az1610958067414WkfOO/devices"

payload={}
headers = {
  'client_id': 'txejpdfda9iwmn5cg2es',
  'access_token': '403f43409951f1ab7f5e100b9153fa5f',
  'sign': '37D842222C92B94B3F8BF489B560AED1600258F43FA644CA2C36DA2164A9DDDA',
  't': '1633075992599',
  'sign_method': 'HMAC-SHA256'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text.encode('utf8'))