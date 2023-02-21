import requests
import time
from datetime import datetime

api_key = "32FYLMVOCRRN"
timezone = "Australia/Perth"

while True:
	response = requests.get(f"http://api.timezonedb.com/v2.1/get-time-zone?key={api_key}&format=json&by=zone&zone={timezone}")
	data = response.json()
	current_time = data["formatted"]
	current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S').strftime('%H:%M:%S %d-%m-%Y')
	print(current_time)
	time.sleep(5)