import argparse
import httplib2
import re
from os import path

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTube(object):
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    def __init__(self, apikey, address=None, port=None):
        self.address = address
        self.port = port
        self.DEVELOPER_KEY = apikey
        if address:
            self.h = httplib2.Http(proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, address, port))
        self.youtube = build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            developerKey=self.DEVELOPER_KEY,
            http=self.h
        )

    async def stream_check(self, ch_id):
        print("checking " + ch_id)
        url = f'https://www.youtube.com/channel/{ch_id}/live'
        h = httplib2.Http(proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, self.address, self.port))
        r, c = h.request(url)
        c = str(c)
        if "offline" not in c: # live now

            st = c.find('"video_id":"') + 12
            ed = st
            while c[ed] != '"':
                ed += 1
            video_id = c[st:ed]
            #print(video_id)
            
            while True:
                try:
                    search_response = self.youtube.videos().list(
                        part='snippet',
                        id=video_id
                    ).execute()
                    break
                except:
                    pass
            res = search_response.get('items', [])
            # print(res)
            if len(res) == 1:
                res = res[0]['snippet']
                return [True, res['channelTitle'], res['title'], res['thumbnails']]
            else:
                return [False]
        else: # offline now
            return [False]

    async def stream_check_search(self, ch_id):
        # Call the search.list method to retrieve results matching the specified
        # query term.
        while True:
            try:
                search_response = self.youtube.search().list(
                    part='snippet',
                    channelId=ch_id,
                    type='video',
                    eventType='live'
                ).execute()
                break
            except:
                pass

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        res = search_response.get('items', [])
        if len(res) == 1:
            res = res[0]['snippet']
            return [True, res['channelTitle'], res['title'], res['thumbnails']]
        else:
            return [False]

    async def channel_search(self, Vtuber_Name: str):
        # Search ytb channel by name
        # Return a list
        #       Cases of success: [True, Channel_Title(str), Channel_Id(str), thumbnails_url(dict)]
        while True:
            try:
                search_response = self.youtube.search().list(
                    part='snippet',
                    q=Vtuber_Name,
                    maxResults=10
                ).execute()
                break
            except:
                pass
        res = search_response.get('items', [])
        if len(res) == 0: # no such Vtuber
            return [False]
        else:
            x = {}
            for item in res:
                id = item['snippet']['channelId']
                if id in x:
                    x[id][1] += 1
                else:
                    x[id] = [item['snippet']['channelTitle'], 1]
                #print(item['snippet']['channelTitle'])

            most_possible_ch_id = res[0]['snippet']['channelId']
            for possible_ch_id in x:
                if x[possible_ch_id][1] > x[most_possible_ch_id][1]:
                    most_possible_ch_id = possible_ch_id
            
            print('selected' + x[most_possible_ch_id][0])

            ch_info = await self.channel_info(most_possible_ch_id)
            return ch_info
            
    
    async def channel_info(self, ch_id: str):
        # Get channel information
        # Return a list
        #       Cases of success: [True, Channel_Title(str), Channel_Id(str), thumbnails_url(dict)]
        while True:
            try:
                search_response = self.youtube.channels().list(
                        part='snippet',
                        id=ch_id
                    ).execute()
                break
            except:
                pass
        res = search_response.get('items', [])
        if len(res) != 1: # channel search error
            return [False]
        else:
            item = res[0]['snippet']
            return [True, ch_id, item['title'], item['thumbnails']]
    
    async def pic_download(self, url, ch_id):
        file_path = path.join(path.dirname(__file__), 'cache', ch_id+'.jpg')
        _, img = self.h.request(url)
        with open(file_path, 'wb') as f:
            f.write(img)
        return file_path

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.

youtube = YouTube('AIzaSyAe9_wDbm3dXxq36aMpEA6IYhYAPow87lo', address='localhost', port=1080)