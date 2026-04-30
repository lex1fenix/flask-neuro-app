import requests

r = requests.get('http://localhost:5000/')
print("Status:", r.status_code)
print("Ответ:", r.text[:100])
