import requests

base_url = "https://cache-money-api.onrender.com/generatebudget"

params = {'text': "I want to spend 20% less"}

response = requests.get(base_url, params=params)

print(response.json())

