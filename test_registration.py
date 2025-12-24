import requests
import json

# Test registration
url = "https://api.jarvisb.app/auth/register"
data = {
    "email": "debug@test.com",
    "password": "test",
    "username": "debug"
}

print("Testing registration...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data)}")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        print("âœ… Success!")
    else:
        print("âŒ Failed")
except Exception as e:
    print(f"Error: {e}")
