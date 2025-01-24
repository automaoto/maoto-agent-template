from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_resolver')
load_dotenv('.env_resolver')

agent = Maoto(open_connection=True)

# optional:
@agent.register_auth_handler()
def auth_handler(element):
    if not isinstance(element, Actioncall):
        raise Exception("This directive can only be used with Actioncall elements.")
    # possibly check if the agent has the rights to send action

@agent.register_action_handler("search_online")
def research(actioncall: Actioncall, parameters) -> str:
    return "He is 100 year old."

@agent.register_bid_handler("search_online")
def bid_search_online(post: Post) -> float:
    print(f"Bid for search_online: {post}")
    return 1.5

@agent.register_bid_handler_fallback()
def bid_handler_fallback(post_reqtest: BidRequest) -> float:
    """This method serves as a fallback for undefined methods."""
    print(f"Bid for action with action id: {post_reqtest.get_action_id()}")
    return 0.5

@agent.register_action_handler_fallback()
def action_fallback(actioncall: Actioncall, parameters) -> str:
    return f"This method serves as a fallback for undefined methods. It serves for acrion with action id: {actioncall.get_action_id()}."

if __name__ == "__main__":
    created_actions = agent.create_actions([
        NewAction(
            name="search_online",
            parameters=json.dumps({'query': 'str'}),
            description="Search online.",
            tags=["search", "online", "search", "engine"],
            cost=0,
            followup=False
        ),
    ])

    agent.start_server(blocking=True)