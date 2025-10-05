import json
from dotenv import load_dotenv
from os import environ
import os
load_dotenv()

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ['how', 'what', 'who', 'where', 'when', 'why', 'which', 'whose', 'whom', 'can you', "what's", "where's", "how's"]
    if any((word + ' ' in new_query for word in question_words)):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + '?'
            return new_query.capitalize()
        new_query += '?'
        return new_query.capitalize()
    if query_words[-1][-1] in ['.', '?', '!']:
        new_query = new_query[:-1] + '.'
        return new_query.capitalize()
    new_query += '.'
    return new_query.capitalize()

def LoadMessages():
    chat_log_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ChatLog.json')
    try:
        with open(chat_log_path, 'r') as f:
            messages = json.load(f)
            if not isinstance(messages, list):
                print(f"Warning: ChatLog.json contains non-list data. Resetting to empty list.")
                return []
            return messages
    except FileNotFoundError:
        print(f"ChatLog.json not found at {chat_log_path}. Creating an empty file.")
        with open(chat_log_path, 'w') as f:
            json.dump([], f)
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding ChatLog.json: {e}. Resetting to empty list.")
        with open(chat_log_path, 'w') as f:
            json.dump([], f)
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading ChatLog.json: {e}. Resetting to empty list.")
        with open(chat_log_path, 'w') as f:
            json.dump([], f)
        return []

def GuiMessagesConverter(messages: list[dict[str, str]]):
    temp = []
    Assistantname = environ['AssistantName']
    Username = environ['NickName']
    for message in messages:
        if message['role'] == 'assistant':
            temp.append(f"""<span class = "Assistant">{Assistantname}</span> : {message['content']}""")
            temp.append('[*end*]')
        elif message['role'] == 'user':
            temp.append(f"""<span class = "User">{Username}</span> : {message['content']}""")
        else:
            temp.append(f"""<span class = "User">{Username}</span> : {message['content']}""")
    return temp