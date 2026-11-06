import os
import requests

APP_ID = os.environ["DISCORD_APPLICATION_ID"]
BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]

# USER_INSTALL = 1; BOT_DM = 1.
command = {
    "name": "wish",
    "description": "Receive your Diwali greeting card",
    "type": 1,
    "integration_types": [1],
    "contexts": [1],
}

url = f"https://discord.com/api/v10/applications/{APP_ID}/commands"
response = requests.post(
    url,
    headers={"Authorization": f"Bot {BOT_TOKEN}"},
    json=command,
    timeout=20,
)
response.raise_for_status()
print("Registered /wish:")
print(response.json())
