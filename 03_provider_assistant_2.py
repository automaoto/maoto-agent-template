import asyncio
from dotenv import load_dotenv
from maoto_agent import *

load_dotenv('.secrets_server')
load_dotenv('.env_server')

# This is how to send a message to the assistant
maoto = Maoto()

async def main():
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

asyncio.run(main())