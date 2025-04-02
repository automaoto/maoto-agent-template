import asyncio
from dotenv import load_dotenv
from maoto_agent import *

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

# Important: the webhook should be only set once when starting the application.
# It is therefore strongly recommended to set it in a dedicated setup workflow (see github workflows)

async def main():
    await maoto.set_webhook()

asyncio.run(main())

