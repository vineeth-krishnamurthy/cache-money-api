import requests

base_url = "https://cache-money-api.onrender.com/generatebudget"

params = {'text': "hello vineeth"}

response = requests.get(base_url, params=params)

print(response.json())

