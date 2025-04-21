import asyncio
from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

async def main():
    try:
        print(await maoto.health_marketplace())
    except Exception:
        print("Marketplace is down.")

    try:
        print(await maoto.health_assistant())
    except Exception:
        print("Assistant is down.")

asyncio.run(main())