
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from enum import Enum

import requests

headers = {
    'sign_method': 'HMAC-SHA256',
    'client_id': 'txejpdfda9iwmn5cg2es',
    't': '1633498170674',
    'mode': 'cors',
    'Content-Type': 'application/json',
    'sign': '320BE35DE30BDD60C5E21295C4C50210E40FA6AEA75A605395AC39DD1727F855',
    'access_token': '795943a8fbc406d29022e1941f046a3b',
}

response = requests.get('https://openapi.tuyaus.com/v1.0/users/az1610958067414WkfOO/devices', headers=headers)


"""url = "https://openapi.tuyaus.com/v1.0/token?grant_type=1"

payload={}
headers = {
    'client_id': 'txejpdfda9iwmn5cg2es',
    'sign': '8D0152E2B32BF529048C4ED6CFE34F547E9B83E6BB312B15B1B7B84516DB0901',
    't': '1633496660037',
    'sign_method': 'HMAC-SHA256'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

def get_request(self):
        apikey = "txejpdfda9iwmn5cg2es"
        apiSecret = "46d6072ffd724e0ba5ebeb5cc6b9dce9"
        token = '8D0152E2B32BF529048C4ED6CFE34F547E9B83E6BB312B15B1B7B84516DB0901'
        
        #url = "https://openapi.tuyaus.com/v1.0/users/az1610958067414WkfOO/devices"
        url = "https://openapi.tuyaus.com/v1.0/token?grant_type=1"
        try:
            r = requests.get(url, auth=HTTPBasicAuth(apikey, apiSecret))
            if r.status_code == requests.codes.ok:
                print(r.content)

                return r.content
            else:
                print("BASpi6u6r.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            print("Error: " + str(e))
        print(r.content)    
    
if __name__ == '__main__':
    
    try:
        pass
        get_request(get_request)
    except KeyboardInterrupt:
        pass"""



url = "https://openapi.tuyaus.com/v1.0/token?grant_type=1"

payload={}
headers = {
    'client_id': 'txejpdfda9iwmn5cg2es',
    'sign': '8D0152E2B32BF529048C4ED6CFE34F547E9B83E6BB312B15B1B7B84516DB0901',
    't': '1633496660037',
    'sign_method': 'HMAC-SHA256'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
# token Get


