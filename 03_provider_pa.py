from maoto_agent import *
from dotenv import load_dotenv

load_dotenv('.secrets_provider') # Should contain MAOTO_API_KEY

agent = Maoto(logging_level=logging.WARNING)

@agent.register_history_handler()
async def history_handler(historyelement: HistoryElement):
    print(f"PA Answer: {historyelement.get_text()}\n")

historyelement = None
while True:
    #uploaded_file = agent.upload_files([Path("./test_audiofile.mp3")])[0]
    input_text = input("Prompt: ")
    new_historyelement = NewHistoryElement(
        text=input_text,
        #file_ids=[uploaded_file.get_file_id()],
        tree_id=historyelement.get_tree_id() if historyelement is not None else None,
        parent_id=historyelement.get_history_id() if historyelement is not None else None,
    )
    historyelement = agent.create_historyelements([new_historyelement])[0]