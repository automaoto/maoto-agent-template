from maoto_agent import *
from dotenv import load_dotenv
import signal
import sys
import time

# Define a signal handler to gracefully exit
def signal_handler(signum, frame):
    print("\nTermination signal received. Exiting...")
    sys.exit(0)

# Register the signal handler for SIGINT and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

load_dotenv('.secrets_status')

agent = Maoto(receive_messages=False)

while True:
    try:
        print("Server is up and running." if agent.check_status() else "Server is down.")
    except Exception:
        print("Server is down.")
    time.sleep(3)