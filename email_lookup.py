import requests

SLACK_API_TOKEN = "your-slack-api-token-here"
EMAIL = "user@example.com"

url = "https://slack.com/api/users.lookupByEmail"
headers = {"Authorization": f"Bearer {SLACK_API_TOKEN}"}
params = {"email": EMAIL}

response = requests.get(url, headers=headers, params=params)
data = response.json()

if data.get("ok"):
    print("User found:", data["user"])
else:
    print("Error:", data.get("error"))
