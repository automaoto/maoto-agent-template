from maoto_agent import *

agent = Maoto(logging_level=logging.ERROR)

# @agent.register_auth_directive
# def auth_directive(element):

    # check if element type is the expected one for this type of agent:
    # for resolver: Actioncall, provider: Response, Personal Asisstant: HistoryElement
    # i.e.:
'''
    if not isinstance(element, Actioncall):
        raise Exception("This directive can only be used with Actioncall elements.")
    '''
    # additionally possibly check if this specific agent has the rights to send element (using element_by_agent = element.get_apikey_id())
'''db = agent.server.get_con()
    try:
        with db.cursor(cursor_factory=DictCursor) as cursor:
            # Get file from database
            cursor.execute("SELECT apikey_id, extension, complete, time FROM files WHERE file_id = %s", (file_id,))
            file = cursor.fetchone()
            file = File(
                file_id=file['file_id'],
                apikey_id=file['apikey_id'],
                extension=file['extension'],
                time=file['time']
            )
    finally:
        agent.server.put_con(db)'''

# Comments to be implemented:
'''
@agent.bid_action("audio_to_text")
def bid_audio_to_text(actioncall: Actioncall) -> float:
    return 1.0

@agent.bid_action_fallback
def bid_action_fallback(actioncall: Actioncall) -> float:
    """This method serves as a fallback for undefined methods."""
    return 0.5
'''

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

# This is just here temporarily, because when using the package in client-mode it is non-blocking.
from time import sleep
sleep(1000)

######### Examples helping your implementation #########
# | | | | | | | | | | | | | | | | | | | | | | | |
# v v v v v v v v v v v v v v v v v v v v v v v v

# Database accesses example:
'''
db = agent.server.get_con()
try:
    with db.cursor(cursor_factory=DictCursor) as cursor:
        # Get file from database
        cursor.execute("SELECT apikey_id, extension, complete, time FROM files WHERE file_id = %s", (file_id,))
        file = cursor.fetchone()
        file = File(
            file_id=file['file_id'],
            apikey_id=file['apikey_id'],
            extension=file['extension'],
            time=file['time']
        )
finally:
    agent.server.put_con(db)
'''

# Logging example:
'''
agent.logger.debug("Debug message")
agent.logger.info("Info message")
agent.logger.warning("Warning message")
agent.logger.error("Error message")
agent.logger.critical("Critical message")
'''

# Error handling example:
'''
try:
    raise Exception("Error message.")
except Exception as e:
    agent.logger.error("Error: %s", e)
    raise Exception("Error message.") # Optional if you wanna show error
'''