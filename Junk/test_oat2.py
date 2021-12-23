import requests

from requests.auth import OAuth1

auth = OAuth1('txejpdfda9iwmn5cg2es', '46d6072ffd724e0ba5ebeb5cc6b9dce9',
        '795943a8fbc406d29022e1941f046a3b', '3fae247738b59a0a3f10f0be39b74fa4')

requests.get('https://openapi.tuyaus.com/v1.0/users/az1610958067414WkfOO/devices', auth=auth) #=HTTPBasicAuth('user', 'pass'))
#<Response [200]>

"""
url = "https://openapi.tuyaus.com/v1.0/token/94af0cd6e038992505f6806c1ddeb2e9"

payload={}
headers = {
  'client_id': 'txejpdfda9iwmn5cg2es',
  'sign': 'BD6249AF527E0F683C699E02233A5BE1A4AF771D205A3589DB628AD3BC1C625A',
  't': '1633837633496',
  'sign_method': 'HMAC-SHA256'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)"""

"""import requests

url = "https://openapi.tuyaus.com/v1.0/users/az1610958067414WkfOO/devices"

payload={}
headers = {
    'client_id': 'txejpdfda9iwmn5cg2es',
    'access_token': 'e875f2f43009a38284ec7db70f8c6588',
    'sign': 'BD6249AF527E0F683C699E02233A5BE1A4AF771D205A3589DB628AD3BC1C625A',
    't': '1633837647951',
    'sign_method': 'HMAC-SHA256'
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)"""
