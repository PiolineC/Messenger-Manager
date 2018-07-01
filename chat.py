class Chat:
    def __init__(self, tid, time_removed, rejoin_time=0):        
        self.thread_id = tid
        self.time_removed = time_removed
        self.rejoin_time = rejoin_time

#TODO
#add minutes parameter for timeouts
#implement message limits that auto kick after a specified amount of messages are sent