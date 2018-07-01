from chat import Chat

class User:
    def __init__(self, uid):        
        self.user_id = uid
        self.chats = {}
        self.timed_chats = {}

    def add_chat(self, chat, timed=False):
        if timed:
            self.timed_chats[chat.thread_id] = chat
        else:
            self.chats[chat.thread_id] = chat
      
    def remove_chat(self, tid, timed=False):
        if timed:
            del self.timed_chats[tid]
        else:
            del self.chats[tid]