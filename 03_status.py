from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_status')
load_dotenv('.env_status')

try:
    agent = Maoto(connection_mode="no_nat")
    status = agent.check_status()
    if not status:
        raise Exception("Server is down.")
except Exception as e:
    print("Server is down.")

print("Server is up.")