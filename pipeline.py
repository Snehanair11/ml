from chatbot.dialogue_manager import handle_message

def run_pipeline(payload: dict):
    """
    Single entry point for prediction + response.
    """

    return handle_message(payload)

