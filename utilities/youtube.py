import argparse
import httplib2

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTube(object):
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    def __init__(self, apikey, address=None, port=None):
        self.DEVELOPER_KEY = apikey
        if address:
            h = httplib2.Http(proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, address, port))
        self.youtube = build(
            self.YOUTUBE_API_SERVICE_NAME,
            self.YOUTUBE_API_VERSION,
            developerKey=self.DEVELOPER_KEY,
            http=h
        )

    def stream_check(self, ch_id):
        # Call the search.list method to retrieve results matching the specified
        # query term.
        search_response = self.youtube.search().list(
            part='snippet',
            channelId=ch_id,
            type='video',
            eventType='live'
        ).execute()

        # Add each result to the appropriate list, and then display the lists of
        # matching videos, channels, and playlists.
        res = search_response.get('items', [])
        if len(res) == 1:
            res = res[0]['snippet']
            return [True, res['channelTitle'], res['title'], res['thumbnails']]
        else:
            return [False]
        '''
        for search_result in search_response.get('items', []):
            # print(search_result)
            print(search_result)
        '''

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
