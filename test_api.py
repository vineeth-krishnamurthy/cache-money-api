import requests
import json

base_url = "https://cache-money-api.onrender.com/generate_chat_response"
# base_url = "http://127.0.0.1:5000/current_spending"

params = {'userID': "Doug"}
params = {'userID': 'Doug', 'text': 'How should I budget next month'}

response = requests.get(base_url, params=params)

print(response.json())

