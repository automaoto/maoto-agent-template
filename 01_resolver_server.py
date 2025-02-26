from maoto_agent import *
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from dotenv import load_dotenv

load_dotenv('.secrets_resolver')
load_dotenv('.env_resolver')

agent = Maoto()

@agent.register_handler("Actioncall", "grab_ride_hauling")
async def actioncall_handler(actioncall: Actioncall):
    print("Actioncall grab_ride_hauling")
    new_response = NewResponse(
        post_id=actioncall.get_post_id(),
        description="The grab ride was booked successfully. It will arrive at your location in 8 minutes."
    )
    await agent.create_responses([new_response])

async def delayed_method(actioncall: Actioncall):
    for i in range(10):
        await asyncio.sleep(1)
        print(f"Count {i+1}/10")
    print("Delayed method")
    await agent.refund_payment(actioncall.get_actioncall_id())

@agent.register_handler("Actioncall", "tada_ride_hauling")
async def actioncall_handler(actioncall: Actioncall):
    print("Actioncall tada_ride_hauling")
    asyncio.create_task(delayed_method(actioncall))
    new_response = NewResponse(
        post_id=actioncall.get_post_id(),
        description="The tada ride was booked successfully. It will arrive at your location in 7 minutes."
    )
    await agent.create_responses([new_response])

@agent.register_handler("Actioncall_fallback")
async def actioncall_handler_fallback(actioncall: Actioncall):
    print("Actioncall fallback")
    new_response = NewResponse(
        post_id=actioncall.get_post_id(),
        description=f"This method with action_id: {actioncall.get_action_id()} is not supported by the agent."
    )
    await agent.create_responses([new_response])

@agent.register_handler("BidRequest", "grab_ride_hauling")
async def bidrequest_handler(bid_request: BidRequest):
    print(f"Bidding")
    new_bid = BidResponse(
        action_id=bid_request.get_action_id(),
        post_id=bid_request.get_post().get_post_id(),
        cost=29.50
    )
    await agent.create_bidresponses([new_bid])

@agent.register_handler("BidRequest", "tada_ride_hauling")
async def bidrequest_handler(bid_request: BidRequest):
    print(f"Bidding")
    new_bid = BidResponse(
        action_id=bid_request.get_action_id(),
        post_id=bid_request.get_post().get_post_id(),
        cost=25.00
    )
    await agent.create_bidresponses([new_bid])

@agent.register_handler("BidRequest_fallback")
async def bidrequest_handler_fallback(bid_request: BidRequest):
    """This method serves as a fallback for undefined methods."""
    print("Bidding fallback")
    new_bid = BidResponse(
        action_id=bid_request.get_action_id(),
        post_id=bid_request.get_post().get_post_id(),
        cost=None
    )
    await agent.create_bidresponses([new_bid])

created_actions = agent.create_actions([
    NewAction(
        name="grab_ride_hauling",
        parameters=json.dumps({'longitude': 'int', 'latitude': 'int', 'destination': 'str'}),
        description="Books a Grab ride.",
        tags=["Grab", "ride hauling"],
        cost=None,
        followup=False
    ),
    NewAction(
        name="tada_ride_hauling",
        parameters=json.dumps({'longitude': 'int', 'latitude': 'int', 'destination': 'str'}),
        description="Books a Tada ride.",
        tags=["Tada", "ride hauling"],
        cost=None,
        followup=False
    ),
])

app = Starlette(
    routes=[
        Route("/maoto_agent", agent.handle_request, methods=["GET", "POST", "OPTIONS"]),
        Route("/healthz", lambda request: JSONResponse({"status": "ok"}), methods=["GET"]),
    ]
)
# execute this with:
# gunicorn -w 2 -k uvicorn.workers.UvicornWorker 01_resolver_server:app --bind 0.0.0.0:8080
# ngrok http --scheme=http --host-header="localhost:8080" 8080

# Note: the webhook should be only set once when starting the application. For this reason a post request is used (i.e. in github actions): see docs
# for local testing of the webhook use local_register_webhooks.py to register the ngrok url with "/maoto_agent" in the end