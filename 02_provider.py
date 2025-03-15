from maoto_agent import *
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.applications import Starlette
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

agent = Maoto()

@agent.register_handler("Response")
async def response_handler(response: Response):
    print(f"Received response:{response}")

# currently not used and not tested:
#uploaded_files = agent.upload_files([Path("./test_audiofile.mp3")])

new_post = NewPost(
    description="Book a grab for me please!",
    context=""
)
agent.fetch_action_info([new_post])

# create a single uuid and get it as a string
new_post = agent.create_posts([NewPost(
    description="Book a grab for me please!",
    context=""
)])

app = Starlette(
    routes=[
        Route("/maoto_agent", agent.handle_request, methods=["GET", "POST", "OPTIONS"]),
        Route("/healthz", lambda request: JSONResponse({"status": "ok"}), methods=["GET"]),
    ]
)
# execute this with:
# gunicorn -w 2 -k uvicorn.workers.UvicornWorker 01_resolver_server:app --bind 0.0.0.0:8080
# ngrok http --scheme=http --host-header="localhost:8080" 8080
