import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")
print(f"Token length: {len(token) if token else 0}")
if token:
    print(f"Token start: {token[:5]}...")
else:
    print("No token found")
