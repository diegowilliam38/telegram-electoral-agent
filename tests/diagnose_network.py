import asyncio
import httpx
import sys

async def check_connection():
    url = "https://api.telegram.org"
    print(f"Testing connection to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            print(f"✅ Status Code: {response.status_code}")
            print(f"✅ Headers: {response.headers}")
    except httpx.ConnectError as e:
        print(f"❌ ConnectError: {e}")
    except Exception as e:
        print(f"❌ Other Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_connection())
