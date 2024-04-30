import requests

base_url = "https://cache-money-api.onrender.com/generatebudget"

params = {'text': "I want to save an extra $100, can you create a budget based on the transaction categories"}

response = requests.get(base_url, params=params)

print(response.json())

