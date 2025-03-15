from dotenv import load_dotenv
import os
from maoto_agent import *

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto_api_key = os.getenv('MAOTO_API_KEY')

# regsiter maoto webhook
agent = Maoto(assistant=False)

agent.set_webhook()
print("Maoto webhook registered")

# Note: the webhook should be only set once when starting the application. For this reason most commonly curl is used (see github action). See docs for more info.

# Note: for local testing of the webhook register the ngrok url with "/maoto_agent" in the end