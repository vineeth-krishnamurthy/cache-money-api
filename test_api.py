import requests

base_url = "https://cache-money-api.onrender.com/average_spending"

params = {'text': "I want to spend 20% less"}

response = requests.get(base_url)

print(response.json())

