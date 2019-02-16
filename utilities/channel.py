from os import path
import pickle

class Vtuber(object):
    vtb_id = str()
    channel_title = str()
    thumbnail_url = dict()
    def __init__(self, ch_id, ch_title, thumbnail_url):
        self.vtb_id = ch_id
        self.channel_title = ch_title
        self.thumbnail_url = thumbnail_url

class Data(object):
    FILE_PATH = path.join(path.dirname(__file__), 'Vtuber.data')
    def __init__(self):
        self.Vtubers = list()
        if path.exists(self.FILE_PATH):
            self.load()
    
    def info(self):
        # Get each vtuber
        return self.Vtubers

    def add_Vtuber(self, vtb: Vtuber):
        self.Vtubers.append(vtb)
        self.store()

    def load(self):
        # Load Vtubers' information from the file and return a list of class Vtuber's instance
        data_list = list()
        with open(self.FILE_PATH, 'rb') as f:
            self.Vtubers = pickle.load(f)

    def store(self):
        # update file
        with open(self.FILE_PATH, 'wb') as f:
            pickle.dump(self.Vtubers, f)
    
    def search(self, ch_id: str):
        for vtb in self.Vtubers:
            if vtb.vtb_id == ch_id:
                return True
        else: return False

database = Data()