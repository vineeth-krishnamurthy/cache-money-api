import requests

base_url = "http://127.0.0.1:5000/generatebudget"

params = {'text': "hello vineeth"}

response = requests.get(base_url, params=params)

print(response.status_code)

