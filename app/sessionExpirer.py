from threading import Thread
import time
from brilliant.objects import GlobalDatabase

class AutoExpirer(Thread):
    """A thread that will automatically invalidate sessions. 
    Daemon thread"""

    def __init__(self, collection_interval=30):
        Thread.__init__(self)
        self.daemon = True
        self.collection_interval = collection_interval
        
    def run(self):
        while True:
            now = time.time()
            
            for key, session in GlobalDatabase.Sessions.items():
                if session in GlobalDatabase.UsedSessions:
                    continue
                if now > session.expire_on:
                    session.delete()
                    
            time.sleep(self.collection_interval)
            