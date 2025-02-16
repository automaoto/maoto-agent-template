from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_resolver')
load_dotenv('.env_resolver')

agent = Maoto()

@agent.register_handler("Actioncall", "grab_ride_hauling")
async def ride_hauling_action_handler(actioncall: Actioncall) -> str:
    print("Actioncall grab_ride_hauling")
    return "The grab ride was booked successfully. It will arrive at your location in 8 minutes."

@agent.register_handler("Actioncall", "tada_ride_hauling")
async def ride_hauling_action_handler(actioncall: Actioncall) -> str:
    print("Actioncall tada_ride_hauling")
    await agent.refund_payment(actioncall.get_actioncall_id())
    return "The tada ride was booked successfully. It will arrive at your location in 7 minutes."

@agent.register_handler("Actioncall_fallback")
async def action_fallback(actioncall: Actioncall) -> str:
    print("Actioncall fallback")
    return f"The ride was booked successfully. It will arrive at your location in 10 minutes."

@agent.register_handler("BidRequest", "grab_ride_hauling")
async def ride_hauling_action_handler(post: Post) -> float:
    print(f"Bidding")
    return 29.50

@agent.register_handler("BidRequest", "tada_ride_hauling")
async def ride_hauling_action_handler(post: Post) -> float:
    print(f"Bidding")
    return 25.00

@agent.register_handler("BidRequest_fallback")
async def bid_handler_fallback(post: Post) -> float:
    """This method serves as a fallback for undefined methods."""
    print("Bidding fallback")
    return None

if __name__ == "__main__":
    created_actions = agent.create_actions([
        NewAction(
            name="grab_ride_hauling",
            parameters=json.dumps({'longitude': 'int', 'latitude': 'int', 'destination': 'str'}), #TODO: change to stacked parameters (longitude, latitude are a pair of current location)
            description="Books a Grab ride.",
            tags=["Grab", "ride hauling"],
            cost=None,
            followup=False
        ),
        NewAction(
            name="tada_ride_hauling",
            parameters=json.dumps({'longitude': 'int', 'latitude': 'int', 'destination': 'str'}), #TODO: change to stacked parameters (longitude, latitude are a pair of current location)
            description="Books a Tada ride.",
            tags=["Tada", "ride hauling"],
            cost=None,
            followup=False
        ),
    ])

    agent.start_server(blocking=True)