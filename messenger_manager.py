from fbchat import Client
from fbchat.models import *
from user import User
from chat import Chat
from random import randint

class MessengerManager(Client):
    users = {}

    def onListening(self):
        info = self.fetchUserInfo(self.uid)[str(self.uid)]
        self.kick_msg = "@" + info.name
        self.join_msg = "/join"

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        #ignore any messages sent by the bot
        if author_id == self.uid:
            return
        #kick the user from a group chat upon request
        if thread_type == ThreadType.GROUP and message_object.text == self.kick_msg:
            self.kick_user(author_id, thread_id)   
            self.reactToMessage(message_object.uid, self.random_react())     
        #add the user back to all kicked chats upon request
        if thread_type == ThreadType.USER and message_object.text == self.join_msg: 
            self.add_user(author_id)            

    def onPeopleAdded(self, added_ids, author_id, thread_id, **kwargs):
        #keep users removed if someone else tries to add them back
        for uid in added_ids:
            if uid in self.users and thread_id in self.users[uid].chats:
                self.removeUserFromGroup(uid, thread_id=thread_id)

    def kick_user(self, uid, tid):
        if uid not in self.users:
            self.track_new_user(uid)  
        user = self.users[uid]
        chat = Chat(tid)
        user.add_chat(chat)
        self.removeUserFromGroup(uid, thread_id=tid)

    def add_user(self, uid):
        if uid not in self.users:
            return
        user = self.users[uid]
        for tid in list(user.chats.keys()):
            self.addUsersToGroup(uid, thread_id=tid)
            user.remove_chat(tid)

    def track_new_user(self, uid):
        new_user = User(uid)
        self.users[uid] = new_user  

    def random_react(self):
        reacts = [MessageReaction.ANGRY, MessageReaction.LOVE, MessageReaction.NO, MessageReaction.SAD, MessageReaction.SMILE, MessageReaction.WOW, MessageReaction.YES]        
        r = randint(0, len(reacts) - 1)
        return reacts[r]