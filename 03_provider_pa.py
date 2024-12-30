from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_provider')

agent = Maoto(logging_level=logging.WARNING, open_connection=True)

@agent.register_auth_handler()
def auth_handler(element):
    if not isinstance(element, HistoryElement):
        raise Exception("This directive can only be used with HistoryElement elements.")
    # possibly check if the agent has the rights to send historyelement

@agent.register_history_handler()
async def history_handler(historyelement: HistoryElement):
    print(f"Assistant: {historyelement.get_text()}\n")

historyelement = None
while True:
    #uploaded_file = agent.upload_files([Path("./test_audiofile.mp3")])[0]
    input_text = input("\n")
    new_historyelement = NewHistoryElement(
        text=input_text,
        #file_ids=[uploaded_file.get_file_id()],
        tree_id=historyelement.get_tree_id() if historyelement is not None else None,
    )
    historyelement = agent.create_historyelements([new_historyelement])[0]