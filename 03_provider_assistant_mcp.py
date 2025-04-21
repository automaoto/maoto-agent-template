from maoto_agent import Maoto
from maoto_agent.mcp import MCPServer
from dotenv import load_dotenv

load_dotenv('.secrets_server')
load_dotenv('.env_server')

maoto = Maoto()

mcp = MCPServer(app=maoto)

# execute this with:
# uvicorn 03_provider_assistant_mcp:maoto --host 0.0.0.0 --port 8080 --workers 2
# MCP Inspector:
# npx @modelcontextprotocol/inspector
# connect to SSE: http://localhost:8080/mcp

# ngrok http --scheme=http --host-header="localhost:8080" 8080