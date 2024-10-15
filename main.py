from chatbot import Chatbot


def chat_in_terminal(chatbot):
    """
    Starts a conversationin the terminal with the chatbot.
    """
    print("Bot params:")
    print(chatbot.chat[-2]["content"])
    print("Starting conversation:")
    print(chatbot.chat[-1]["content"])
    while True:
        user_input = input("")
        if not handle_user_input(chatbot, user_input):
            break


def handle_user_input(chatbot, user_input):
    """
    Propcess the user input when chatting in the terminal.
    """
    match user_input.lower():
        case "exit" | "quit":
            print("Ending the session. Goodbye!")
            return False
        case _:
            user_message = {
                "role": "user",
                "content": user_input,
            }
            chatbot.add_message(user_message)
            chatbot.check_time(new_check_chain=True)
            assistant_message = chatbot.get_response()
            chatbot.add_message(assistant_message)
            print(assistant_message["content"])
            return True


if __name__ == "__main__":
    bot = Chatbot("Oliver", "ophelia")
    chat_in_terminal(bot)
