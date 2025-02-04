from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_provider')
load_dotenv('.env_provider')

agent = Maoto()

@agent.register_handler("Response")
async def response_handler(response: Response):
    print(f"Received response:{response}")

#uploaded_files = agent.upload_files([Path("./test_audiofile.mp3")])

# create a single uuid and get it as a string
new_post = agent.create_posts([NewPost(
    description="Book a grab for me please!",
    context=""
)])

agent.start_server(blocking=True)
