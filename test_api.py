import requests

base_url = "https://cache-money-api.onrender.com/average_spending"

params = {'userID': "Doug"}

response = requests.get(base_url, params=params)

print(response.json())

