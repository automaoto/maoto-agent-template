from maoto_agent import *
import shutil
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

agent = Maoto()

# Comments to be implemented:
@agent.register_handler("BidRequest", "audio_to_text")
async def bid_audio_to_text(post: Post) -> float:
    print(f"Bid for audio_to_text: {post}")
    return 1.0

@agent.register_handler("BidRequest_fallback")
async def bid_handler_fallback(post_reqtest: BidRequest) -> float:
    """This method serves as a fallback for undefined methods."""
    print(f"Bid for action with action id: {post_reqtest.get_action_id()}")
    return 0.5

@agent.register_handler("Actioncall", "audio_to_text")
async def audio_to_text(actioncall: Actioncall, parameters) -> str:
    
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

@agent.register_handler("Actioncall_fallback")
async def action_fallback(actioncall: Actioncall, parameters) -> str:
    return f"This method serves as a fallback for undefined methods. It serves for acrion with action id: {actioncall.get_action_id()}."

if __name__ == "__main__":
    created_actions = agent.create_actions([
        NewAction(
            name="audio_to_text",
            parameters=json.dumps({'audio_file_id': 'str'}),
            description="Transform audio file to text.",
            tags=["convert", "audio", "text", "transform", "file"],
            cost=None,
            followup=False
        ),
    ])

    agent.start_server(blocking=True)