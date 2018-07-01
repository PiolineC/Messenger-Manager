from apscheduler.schedulers.background import BackgroundScheduler
from fbchat import Client
from fbchat.models import *
from random import randint
from user import User
from chat import Chat
import pickle
import re
import time


class MessengerManager(Client):        
    def onListening(self):
        info = self.fetchUserInfo(self.uid)[str(self.uid)]
        self.kick_msg = "@" + info.name
        self.join_msg = "/join"
        self.load_user_data()

        self.hour_match = r"(\d{1,2}) ?h(?:ours?)?"
        self.min_match = r"(\d{1,2}) ?min(?:ute)?s?" #to be implemented

        scheduler = BackgroundScheduler()
        scheduler.add_job(self.process_timeouts, "interval", minutes=1)
        scheduler.start()

    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        #ignore any messages sent by the bot
        if author_id == self.uid:
            return

        command = message_object.text

        #kick the user from a group chat upon request
        if command.startswith(self.kick_msg) and thread_type == ThreadType.GROUP:            
            current_time = int(time.time())            
            args = command[len(self.kick_msg):].strip()      
            timeout = re.fullmatch(self.hour_match, args, flags=re.IGNORECASE)
            if timeout:
                duration = int(timeout.group(1))
                if duration > 0 and duration <= 24:
                    rejoin_time = current_time + duration * 3600
                    self.kick_user(author_id, thread_id, current_time, rejoin_time) 
                    self.reactToMessage(message_object.uid, self.random_react())   
                else:
                    self.reactToMessage(message_object.uid, MessageReaction.NO)     
            else:
                self.kick_user(author_id, thread_id, current_time)   
                self.reactToMessage(message_object.uid, self.random_react())     

        #add the user back to all kicked chats upon request
        if thread_type == ThreadType.USER and message_object.text == self.join_msg: 
            self.add_back_user(author_id)            

    def onPeopleAdded(self, added_ids, author_id, thread_id, **kwargs):
        #keep users removed if someone else tries to add them back
        for uid in added_ids:
            if uid in self.users:
                user = self.users[uid]
                if thread_id in user.chats or thread_id in user.timed_chats:
                    self.removeUserFromGroup(uid, thread_id=thread_id)

    def kick_user(self, uid, tid, time_removed, time_to_rejoin=0):
        if uid not in self.users:
            self.track_new_user(uid)  
        user = self.users[uid]
        if time_to_rejoin != 0:
            chat = Chat(tid, time_removed, rejoin_time=time_to_rejoin)
            user.add_chat(chat, timed=True)
        else:
            chat = Chat(tid, time_removed) 
            user.add_chat(chat)
        self.removeUserFromGroup(uid, thread_id=tid)
        self.save_to_file()

    def add_back_user(self, uid):
        if uid not in self.users:
            return
        user = self.users[uid]
        for tid in list(user.chats.keys()):            
            user.remove_chat(tid)
            self.addUsersToGroup(uid, thread_id=tid)
            self.save_to_file()

    def track_new_user(self, uid):
        new_user = User(uid)
        self.users[uid] = new_user  
        self.save_to_file()

    def random_react(self):
        reacts = [MessageReaction.ANGRY, MessageReaction.LOVE, MessageReaction.SAD, MessageReaction.SMILE, MessageReaction.WOW, MessageReaction.YES]        
        r = randint(0, len(reacts) - 1)
        return reacts[r]
    
    def process_timeouts(self):
        print(self.users)
        for user in list(self.users.values()):
            for tc in list(user.timed_chats.values()):
                if tc.rejoin_time - time.time() <= 0:                    
                    user.remove_chat(tc.thread_id, timed=True)
                    self.addUsersToGroup(user.user_id, thread_id=tc.thread_id)
                    self.save_to_file()
    
    def load_user_data(self):
        try:
            with open("user_data.pickle", "rb") as file:
                self.users = pickle.load(file)
        except FileNotFoundError:
            self.users = {}
    
    def save_to_file(self):
        with open("user_data.pickle", "wb") as file:
            pickle.dump(self.users, file)