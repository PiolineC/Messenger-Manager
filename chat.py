class Chat:
    def __init__(self, tid, cr=False, tr=False, ml=0, ttr=None):        
        self.thread_id = tid
        self.chat_restricted = cr
        self.time_restricted = tr
        self.msg_limit = ml
        self.time_to_rejoin = ttr

#TODO
#implement timeouts that allow users to leave for a specified period of time
#optional "strict mode" which force kicks the user until that time
#implement message limits that auto kick after a specified amount of messages are sent