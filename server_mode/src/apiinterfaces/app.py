from time import sleep
from maoto_agent import *

agent = Maoto()

@agent.register_action_handler("calendar")
def calendar(actioncall: Actioncall, parameters) -> str:
    return "Today is 18. October 2024."

@agent.register_action_handler_fallback()
def action_fallback(actioncall: Actioncall, parameters) -> str:
    return f"This method serves as a fallback for undefined methods. It serves for acrion with action id: {actioncall.get_action_id()}."

if __name__ == "__main__":
    created_actions_with_methods = agent.create_actions([
        NewAction(
            name="calendar",
            parameters=json.dumps({}),
            description="Returns the current date.",
            tags=["date", "calendar", "info"],
            cost=None,
            followup=False
        )
    ])
    
sleep(1000)