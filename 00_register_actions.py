from dotenv import load_dotenv
import os
from maoto_agent import *

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto_api_key = os.getenv('MAOTO_API_KEY')

# regsiter maoto webhook
agent = Maoto(assistant=False)

# following is temporarily moved somewhere else

# registeres_actions: list[Action] = agent.get_own_actions()
# registered_actions = [action.get_name() for action in registeres_actions]
# print("Registered actions:", registered_actions)

# agent.delete_actions([action.get_action_id() for action in registeres_actions])
# print("Deleted all registered actions")

# created_actions = agent.create_actions([
#     NewAction(
#         name="grab_ride_hailing",
#         parameters=json.dumps({'longitude': 'int', 'latitude': 'int', 'destination': 'str'}),
#         description="Books a Grab ride.",
#         tags=["Grab", "ride hailing"],
#         cost=None,
#         followup=False
#     ),
#     NewAction(
#         name="tada_ride_hailing",
#         parameters=json.dumps({'longitude': 'int', 'latitude': 'int', 'destination': 'str'}),
#         description="Books a Tada ride.",
#         tags=["Tada", "ride hailing"],
#         cost=None,
#         followup=False
#     ),
# ])
