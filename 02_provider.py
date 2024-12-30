from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_provider')

agent = Maoto(open_connection=True)

@agent.register_auth_handler()
def auth_handler(element):
    if not isinstance(element, Response):
        raise Exception("This directive can only be used with Response elements.")
    # possibly check if the agent has the rights to send response

@agent.register_response_handler()
async def response_handler(response: Response):
    print(f"Received response:{response}")

#uploaded_files = agent.upload_files([Path("./test_audiofile.mp3")])

# create a single uuid and get it as a string
new_post = agent.create_posts([NewPost(
    description="Book a grab for me please!",
    context=""
)])

agent.start_server(blocking=True)
