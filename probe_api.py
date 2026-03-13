import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "instagram-scraper-20251.p.rapidapi.com"

# The endpoint from user's snippet
url = f"https://{RAPIDAPI_HOST}/postdetail/"

headers = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type": "application/json"
}

# Testing with a public reel link
querystring = {"code_or_url": "https://www.instagram.com/reel/DV0mZKTEajj/"}

print(f"Sending GET request to {url} with params: {querystring}")
try:
    response = requests.get(url, headers=headers, params=querystring)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("SUCCESS! Looking for video URLs in response...")
        
        def find_mp4_urls(obj):
            urls = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == 'url' and isinstance(v, str) and ('.mp4' in v or 'video' in v):
                        urls.append(v)
                    elif k == 'video_url' and isinstance(v, str):
                        urls.append(v)
                    else:
                        urls.extend(find_mp4_urls(v))
            elif isinstance(obj, list):
                for item in obj:
                    urls.extend(find_mp4_urls(item))
            return urls
            
        found_urls = find_mp4_urls(data)
        print(f"Found {len(found_urls)} video URLs")
        if found_urls:
            print(f"First URL: {found_urls[0][:100]}...")
        else:
            print("No video URLs found. Dumping top-level keys:")
            if 'data' in data:
                print(f"Keys in data: {data['data'].keys() if isinstance(data['data'], dict) else type(data['data'])}")
            else:
                print(f"Top keys: {data.keys()}")
    else:
        print(f"Error Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")

