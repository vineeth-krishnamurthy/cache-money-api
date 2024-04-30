import requests

base_url = "http://127.0.0.1:5000/lowercase"

params = {'text': "STOP PLAYING WITH EM VINEETH"}

response = requests.get(base_url, params=params)

print(response.json())

