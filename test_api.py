import requests

base_url = "https://cache-money-api.onrender.com/generatebudget"

params = {'text': "I want to save $100 next month"}

response = requests.get(base_url, params=params)

print(response.json())

