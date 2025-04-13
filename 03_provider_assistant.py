from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

# Receiving assistant messages
@maoto.register_handler(PAUserMessage)
def pausermessage_handler(pausermessage: PAUserMessage):
    ui_id = pausermessage.ui_id
    text = pausermessage.text
    # this is the message to the user

# This is how to send a message to the assistant
"""
maoto.send_to_assistant(
    PAUserResponse(
        ui_id=str(uuid.uuid4()),
        text="Please confirm your booking.",
    )
)
"""

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

# This is how to put the assistant into technical support mode
"""
maoto.send_to_assistant(
    PASupportRequest(
        ui_id=str(uuid.uuid4()),
        text="Please provide your current location.",
    )
)
"""

# This is how to reset the assistant conversation for the specific user
"""
maoto.send_to_assistant(
    PANewConversation(
        ui_id=str(uuid.uuid4()),
    )
)
"""

# execute this with:
# uvicorn 02_provider_assistant:maoto --host 0.0.0.0 --port 8080 --workers 2
# ngrok http --scheme=http --host-header="localhost:8080" 8080