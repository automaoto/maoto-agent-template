from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

# Receiving assistant messages
@maoto.register_handler(PAUserMessage)
async def pausermessage_handler(pausermessage: PAUserMessage):
    print(f"Received message from user {pausermessage.ui_id}: {pausermessage.text}")
    
    await maoto.send_to_assistant(
        PAUserResponse(
            ui_id=str(uuid.uuid4()),
            text="Tell me a joke!",
        )
    )

    # This is how to put the assistant into technical support mode
    """
    await maoto.send_to_assistant(
        PASupportRequest(
            ui_id=str(uuid.uuid4()),
            text="Please provide your current location.",
        )
    )
    """

    # This is how to reset the assistant conversation for the specific user
    """
    await maoto.send_to_assistant(
        PANewConversation(
            ui_id=str(uuid.uuid4()),
        )
    )
    """

# To handle the PALocationRequest send by the assistant and allow ui integration:
'''
@maoto.register_handler(PALocationRequest)
async def palocationrequest_handler(palocationrequest: PALocationRequest):
    # get location from user through user interface
    
    await maoto.send_to_assistant(
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