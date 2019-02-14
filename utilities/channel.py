from os import path
import pickle

class Vtuber(object):
    __vtb_id = str()
    def __init__(self, ch_id):
        self.__vtb_id = ch_id
    @property
    def vtb_id(self):
        return self.__vtb_id
    
    @vtb_id.setter
    def vtb_id(self, ch_id):
        self.__vtb_id = ch_id

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

database = Data()