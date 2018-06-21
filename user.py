from chat import Chat

class User:
    def __init__(self, uid):        
        self.uid = uid
        self.chats = {}

    def add_chat(self, chat):
        self.chats[chat.thread_id] = chat

    def remove_chat(self, tid):
        del self.chats[tid]