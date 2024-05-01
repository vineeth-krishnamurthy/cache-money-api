import requests
import json

base_url = "https://cache-money-api.onrender.com/current_spending"
# base_url = "http://127.0.0.1:5000/current_spending"

params = {'userID': "Doug"}

response = requests.get(base_url, params=params)

print(response.json())

