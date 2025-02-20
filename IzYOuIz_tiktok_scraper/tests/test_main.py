import requests

# Define the payload
payload = {
    "search_type": "trending",  # or "userid" or "hashtag"
    "search_query": "",         # leave empty for trending
    "max_videos": 2
}

# Send the POST request
url = "http://127.0.0.1:8000/scrape-and-download/"
headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()       # Parse the JSON response
    print("Response:", data)
except requests.exceptions.RequestException as error:
    print("Error:", error)
