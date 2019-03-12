import argparse
import httplib2
import aiohttp
import re
from os import path
from datetime import datetime, timedelta
from aiogoogle import Aiogoogle
import sys

class YouTube(object):
    def __init__(self, api_key, address=None, port=None):
        self.proxy = f'http://{address}:{str(port)}' if address and port else None
        self.api_key = api_key

    async def stream_check(self, channel_id: str, channel_title: str):
        live_url = f'https://www.youtube.com/channel/{channel_id}/live'
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(live_url, proxy=self.proxy) as resp:
                        c = await resp.text()
                break
            except:
                pass
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
                    async with Aiogoogle(api_key=self.api_key) as google:
                        youtube = await google.discover('youtube', 'v3')
                        search_response = await google.as_api_key(
                            youtube.videos.list(
                                part='snippet',
                                id=video_id
                            )
                        )
                    break
                except TypeError:
                    raise TypeError
                except:
                    pass
            res = search_response.get('items', [])
            if len(res) == 1:
                res = res[0]['snippet']
                return [True, res['channelTitle'], res['title'], res['thumbnails']]
            else:
                return [False]
        else: # offline now
            return [False]

    async def channel_search(self, Vtuber_Name: str):
        # Search ytb channel by name
        # Return a list
        #       Cases of success: [True, Channel_Id(str), Channel_Title(str), thumbnails_url(dict)]
        while True:
            try:
                async with Aiogoogle(api_key=self.api_key) as google:
                    youtube = await google.discover('youtube', 'v3')
                    search_response = await google.as_api_key(
                        youtube.search.list(
                            part='snippet',
                            q=Vtuber_Name,
                            maxResults=10
                        )
                    )
                break
            except TypeError:
                raise TypeError
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

            most_possible_channel_id = res[0]['snippet']['channelId']
            for possible_channel_id in x:
                if x[possible_channel_id][1] > x[most_possible_channel_id][1]:
                    most_possible_channel_id = possible_channel_id
            
            print(f'{x[most_possible_channel_id][0]} selected')

            ch_info = await self.channel_info(most_possible_channel_id)
            return ch_info
            
    
    async def channel_info(self, channel_id: str):
        # Get channel information
        # Return a list
        #       Cases of success: [True, Channel_Id(str), Channel_Title(str), thumbnails_url(dict)]
        while True:
            try:
                async with Aiogoogle(api_key=self.api_key) as google:
                    youtube = await google.discover('youtube', 'v3')
                    search_response = await google.as_api_key(
                        youtube.channels.list(
                            part='snippet',
                            id=channel_id
                        )
                    )
                break
            except TypeError:
                raise TypeError
            except:
                pass
        res = search_response.get('items', [])
        if len(res) != 1: # channel search error
            return [False]
        else:
            item = res[0]['snippet']
            return [True, channel_id, item['title'], item['thumbnails']]

    async def uploaded_video_list(self, channel_id: str):
        while True:
            try:
                async with Aiogoogle(api_key=self.api_key) as google:
                    youtube = await google.discover('youtube', 'v3')
                    search_response = await google.as_api_key(
                        youtube.channels.list(
                            part='contentDetails',
                            id=channel_id
                        )
                    )
                break
            except TypeError:
                raise TypeError
            except:
                pass
        res = search_response.get('items', [])
        playlist = res[0]['contentDetails']['relatedPlaylists']['uploads']
        return playlist
    
    async def video_list(self, playlist, maxresult=5):
        while True:
            try:
                async with Aiogoogle(api_key=self.api_key) as google:
                    youtube = await google.discover('youtube', 'v3')
                    search_response = await google.as_api_key(
                        youtube.playlistItems.list(
                            part='snippet',
                            playlistId=playlist,
                            maxResults=maxresult
                        )
                    )
                break
            except TypeError:
                raise TypeError
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
    
    async def channel_statistics(self, channel_id: str):
        # 'viewCount', 'commentCount', 'subscriberCount', 'hiddenSubscriberCount', 'videoCount'
        while True:
            try:
                async with Aiogoogle(api_key=self.api_key) as google:
                    youtube = await google.discover('youtube', 'v3')
                    search_response = await google.as_api_key(
                        youtube.channels.list(
                            part='statistics',
                            id=channel_id
                        )
                    )
                break
            except TypeError:
                raise TypeError
            except:
                pass
        res = search_response.get('items', [])
        assert len(res) == 1
        return res[0]['statistics']
    
    async def subCount(self, channel_id: str):
        res = await self.channel_statistics(channel_id)
        assert res['hiddenSubscriberCount'] == False
        return int(res['subscriberCount'])

if len(sys.argv) < 2:
    exit('no api key')
youtube = YouTube(sys.argv[1], address='127.0.0.1', port=1080)