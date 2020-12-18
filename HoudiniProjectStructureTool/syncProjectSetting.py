import requests
import json

url = "http://maps.googleapis.com/maps/api/geocode/json?address=googleplex&sensor=false"
#proxy = {'http': 'http://okapi.tnn:14240', 'https': 'https://okapi.tnn:14240'}
result = requests.get(url, proxies=proxy)
data = result.json()

print (data['status'])
