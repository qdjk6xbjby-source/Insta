import requests
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

print(f"Key: {RAPIDAPI_KEY[:5]}...{RAPIDAPI_KEY[-5:] if RAPIDAPI_KEY else 'None'}")
print(f"Host: {RAPIDAPI_HOST}")

url = f"https://{RAPIDAPI_HOST}/instagram/download"
querystring = {"url": "https://www.instagram.com/reel/DV0mZKTEajj/"}

headers = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST
}

print("Sending request...")
response = requests.get(url, headers=headers, params=querystring)

print(f"Status Code: {response.status_code}")
try:
    print(f"Response JSON: {response.json()}")
except Exception as e:
    print(f"Response Text: {response.text}")
