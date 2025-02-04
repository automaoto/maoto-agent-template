from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_resolver')
load_dotenv('.env_resolver')

agent = Maoto()

@agent.register_handler("Actioncall", "grab_ride_hauling")
async def ride_hauling_action_handler(actioncall: Actioncall) -> str:
    print(actioncall.get_parameters())
    return "The grab ride was booked successfully. It will arrive at your location in 8 minutes."

@agent.register_handler("Actioncall_fallback")
async def action_fallback(actioncall: Actioncall) -> str:
    print(actioncall.get_parameters())
    return f"This method with action_id: {actioncall.get_action_id()} is not supported by the agent."

@agent.register_handler("BidRequest", "grab_ride_hauling")
async def ride_hauling_action_handler(post: Post) -> float:
    print(f"Bidding")
    return 0.0

@agent.register_handler("BidRequest_fallback")
async def bid_handler_fallback(post_reqtest: BidRequest) -> float:
    """This method serves as a fallback for undefined methods."""
    print(f"Bid for action with action id: {post_reqtest.get_action_id()}")
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
    ])

    agent.start_server(blocking=True)