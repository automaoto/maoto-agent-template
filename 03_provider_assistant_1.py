from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

# Receiving assistant messages
@maoto.register_handler(PAUserMessage)
def pausermessage_handler(pausermessage: PAUserMessage):
    print(f"Received message from user {pausermessage.ui_id}: {pausermessage.text}")
    # this is the message to the user

# To handle the PALocationRequest send by the assistant and allow ui integration:
'''
@maoto.register_handler(PALocationRequest)
def palocationrequest_handler(palocationrequest: PALocationRequest):
    # get location from user through user interface
    
    maoto.send_to_assistant(
        PALocationResponse(
            ui_id=str(uuid.uuid4()),
            location=Location(
                longitude=106.845599,
                latitude=-6.208763
            ),
        )
    )
'''

# execute this with:
# uvicorn 03_provider_assistant_1:maoto --host 0.0.0.0 --port 30000 --workers 2
# ngrok http --scheme=http --host-header="localhost:8080" 8080