from maoto_agent import *
import numpy as np
import shutil
from dotenv import load_dotenv

load_dotenv('.secrets_resolver') # Should contain MAOTO_API_KEY

agent = Maoto()

# user_database = np.array([["provider1", "password1", None], ["provider2", "password2", "2"], [None, None, "3"]])

# class MyAuthenticateProvider(AuthenticateProvider):
#     def authenticate(self, username: str, password: str, maoto_user_id) -> bool:
#         for user in user_database:
#             if user[0] == username and user[1] == password:
#                 user[2] = maoto_user_id
#                 return True
#         return False
        
#     def new_user(self, apikey_id: str) -> bool:
#         for user in user_database:
#             if user[2] == apikey_id:
#                 return False
#         user_database = np.append(user_database, np.array([[None, None, apikey_id]]), axis=0)
#         return True

# agent.init_authentication(MyAuthenticateProvider())

# @agent.bid_action("audio_to_text")
# def bid_audio_to_text(actioncall: Actioncall) -> float:
#     return 1.0

@agent.register_action_handler("audio_to_text")
def audio_to_text(actioncall: Actioncall, parameters) -> str:
    
    audio_file_id = json.loads(parameters)['audio_file_id']
    try:
        audio_file = agent.download_missing_files([audio_file_id])[0]
        new_audio_file_path = (agent.download_dir / str(audio_file.get_file_id())).with_suffix(audio_file.get_extension())
        text_outputs_dir = Path("text_outputs")
        text_outputs_dir.mkdir(exist_ok=True)
        new_file_path = (text_outputs_dir / str(uuid.uuid4())).with_suffix(".txt")

        # Simulate conversion
        new_text_file_path = agent.working_dir / new_file_path
        shutil.copy('text_output.txt',  new_text_file_path)
        
        text_output_file = agent.upload_files([new_file_path])[0]

        # remove temporary files
        new_text_file_path.unlink()
        new_audio_file_path.unlink()

        return f"Successfully converted audio file {audio_file_id} to text file {text_output_file.get_file_id()}."

    except Exception as e:
       return f"Failed to convert audio file {audio_file_id} to text. Try again later."

# @agent.bid_action_fallback
# def bid_action_fallback(actioncall: Actioncall) -> float:
#     return 0.5

@agent.register_action_handler_fallback()
def action_fallback(actioncall: Actioncall, parameters) -> str:
    return f"This method serves as a fallback for undefined methods. It serves for acrion with action id: {actioncall.get_action_id()}."

if __name__ == "__main__":
    created_actions_with_methods = agent.create_actions([
        NewAction(
            name="audio_to_text",
            parameters=json.dumps({'audio_file_id': 'str'}),
            description="Transform audio file to text.",
            tags=["convert", "audio", "text", "transform", "file"],
            cost=None,
            followup=False
        )
    ])
    created_actions_without_methods = agent.create_actions([
        NewAction(
            name="research",
            parameters=json.dumps({'topic': 'str'}),
            description="Research on a specific topic.",
            tags=["research", "topic"],
            cost=1.0,
            followup=False
        )
    ])
