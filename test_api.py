import requests

base_url = "https://cache-money-api.onrender.com/api/generatebudget"

params = {'text': "I want to save $100 next month"}

response = requests.get(base_url, params=params)

print(response.json())

