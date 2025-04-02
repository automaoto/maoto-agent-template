import asyncio
from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

async def main():
    try:
        status_marketplace = await maoto.check_status_marketplace()
        if not status_marketplace:
            print("Marketplace is down.")
    except Exception as e:
        print("Marketplace is down.")

    try:
        status_assistant = await maoto.check_status_assistant() # note: assistant temporarily not publicly available to save cost
        if not status_assistant:
            print("Assistant is down.")
    except Exception as e:
        print("Assistant is down.")

print("Server is up.")

asyncio.run(main())