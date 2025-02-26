from dotenv import load_dotenv
import os
from maoto_agent import *
from telegram import Bot
import asyncio

load_dotenv(".secrets_local_webhook")

maoto_api_key = os.getenv('MAOTO_API_KEY')

maoto_agent_url = os.getenv('MAOTO_AGENT_URL')

# regsiter maoto webhook
agent = Maoto(assistant=False)
agent.set_webhook()
print("Maoto webhook registered")
