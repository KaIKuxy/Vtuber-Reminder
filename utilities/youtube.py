import argparse
import httplib2
import aiohttp
import re
from os import path
from datetime import datetime, timedelta

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

    async def stream_check(self, ch_id: str, channel_title: str):
        url = f'https://www.youtube.com/channel/{ch_id}/live'
        # h = httplib2.Http(proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, self.address, self.port))
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, proxy='http://localhost:1080') as resp:
                        c = await resp.text()
                        #print("get")
                break
            except:
                pass
        '''while True:
            try:
                r, c = h.request(url)
                break
            except:
                pass'''
        c = str(c)
        if "offline" not in c: # live now

            st = c.find('"video_id":"') + 12
            ed = st
            while c[ed] != '"':
                ed += 1
            video_id = c[st:ed]
            if video_id[-1] == '=':
                return [False]
            print(f"{channel_title} is online")
            while True:
                try:
                    #print(video_id)
                    #print(ch_id)
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

    async def stream_check_search(self, ch_id: str):
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
        #       Cases of success: [True, Channel_Id(str), Channel_Title(str), thumbnails_url(dict)]
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
        #       Cases of success: [True, Channel_Id(str), Channel_Title(str), thumbnails_url(dict)]
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
    
    async def pic_download(self, url: str, ch_id: str):
        file_path = path.join(path.dirname(__file__), 'cache', ch_id+'.jpg')
        _, img = self.h.request(url)
        with open(file_path, 'wb') as f:
            f.write(img)
        return file_path

    async def uploaded_video_list(self, ch_id: str):
        while True:
            try:
                search_response = self.youtube.channels().list(
                        part='contentDetails',
                        id=ch_id
                    ).execute()
                break
            except:
                pass
        res = search_response.get('items', [])
        playlist = res[0]['contentDetails']['relatedPlaylists']['uploads']
        return playlist
    
    async def video_list(self, playlist, maxresult=5):
        while True:
            try:
                search_response = self.youtube.playlistItems().list(
                        part='snippet',
                        playlistId=playlist,
                        maxResults=maxresult
                    ).execute()
                break
            except:
                pass
        res = search_response.get('items', [])
        return res
    
    async def newest_video(self, playlist, oldLatestTime):
        # get new videos published after oldLatestTime
        res = await self.video_list(playlist, maxresult=2 if oldLatestTime == datetime.min else 5)
        newLatestTime = oldLatestTime
        video_list = []
        for video in res:
            Time = datetime.strptime(video['snippet']['publishedAt'],'%Y-%m-%dT%H:%M:%S.%fZ')
            if Time > oldLatestTime:
                print("new video")
                newLatestTime = max(newLatestTime, Time)
                video_list.append(video['snippet'])
        return [video_list, newLatestTime]

    async def videos_of_day(self, playlist, today=True):
        res = await self.video_list(playlist)
        video_list = []
        for video in res:
            Time = datetime.strptime(video['snippet']['publishedAt'],'%Y-%m-%dT%H:%M:%S.%fZ')
            if (datetime.utcnow()+timedelta(hours=9)-timedelta(days=not today)).date() == (Time + timedelta(hours=9)).date():
                video_list.append(video['snippet'])
        return video_list
    
    async def channel_statistics(self, ch_id: str):
        # 'viewCount', 'commentCount', 'subscriberCount', 'hiddenSubscriberCount', 'videoCount'
        while True:
            try:
                search_response = self.youtube.channels().list(
                        part='statistics',
                        id=ch_id
                    ).execute()
                break
            except:
                pass
        res = search_response.get('items', [])
        assert len(res) == 1
        return res[0]['statistics']
    
    async def subCount(self, ch_id: str):
        res = await self.channel_statistics(ch_id)
        assert res['hiddenSubscriberCount'] == False
        return int(res['subscriberCount'])

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.

youtube = YouTube('', address='127.0.0.1', port=1080)