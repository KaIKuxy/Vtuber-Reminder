from PIL import Image, ImageDraw, ImageFont
import httplib2
from io import BytesIO
from datetime import datetime
from os import path
import asyncio

WIDTH = 1000
VTB_INT = 30
VIDEO_INT = 20
INFO_INT = 10
VTB_NUM = 5
http = httplib2.Http(proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, "localhost", 1080))

async def uploaded_video_img(vtb_videos):
    files = []
    start = 0
    Len = len(vtb_videos)
    cnt = 0
    tasks = []
    while start < Len:
        tasks.append((start, min(Len, start+VTB_NUM), cnt))
        start += VTB_NUM
        cnt += 1
    tasks = [create_img(vtb_videos[task[0]:task[1]], task[2], files) for task in tasks]
    _, _ = await asyncio.wait(tasks)
    return files

async def create_img(vtb_videos, id, files):
    # [[channel_title, thumbnail, [[video1_title, video1_thumbnail], ....], ...]]
    '''
    vtb_videos = [
        [
            'KMNZ LIZ', {},
            [
                [
                    "ロキ - みきとP(Cover) / KMNZ LIZ",
                    "https://i.ytimg.com/vi/EIbvKSUeta0/hqdefault.jpg"
                    ], 
                [
                    "ロキ - みきとP(Cover) / KMNZ LIZ",
                    "https://i.ytimg.com/vi/EIbvKSUeta0/hqdefault.jpg"
                    ],
                [
                    "ロキ - みきとP(Cover) / KMNZ LIZ",
                    "https://i.ytimg.com/vi/EIbvKSUeta0/hqdefault.jpg"
                    ]
            ]
        ],
        [
            'ドーラ', {},
            [
                [
                    "【3/6 第9話】TVアニメ「バーチャルさんはみている」をみているドレイク【にじさんじ】",
                    "https://i.ytimg.com/vi/zT7Ojv_7ISc/hqdefault.jpg"
                    ], 
                [
                    "【3/6 第9話】TVアニメ「バーチャルさんはみている」をみているドレイク【にじさんじ】",
                    "https://i.ytimg.com/vi/zT7Ojv_7ISc/hqdefault.jpg"
                    ]
            ]
        ],
        [
            '本間ひまわり - Himawari Honma -', {},
            [
                [
                    "ロキ - みきとP(Cover) / KMNZ LIZ",
                    "https://i.ytimg.com/vi/EIbvKSUeta0/hqdefault.jpg"
                    ]
            ]
            ]
    ]
    '''
    font_channel = ImageFont.truetype('UDDigiKyokashoN-R.ttc', 30)
    font_video = ImageFont.truetype('BIZ-UDGothicR.ttc', 20)
    start = 50
    for vtb in vtb_videos:
        w, h = font_channel.getsize(vtb[0])
        start += h
        for video in vtb[-1]:
            start += VIDEO_INT
            title_w, title_h = font_video.getsize(video[0])
            start += title_h + INFO_INT
            start += 360
        start += VTB_INT

    background = Image.open(path.join(path.dirname(__file__), 'back.jpg'))
    img = Image.new('RGBA', (WIDTH, start + background.size[1]), (254, 248, 232, 255))
    draw = ImageDraw.Draw(img)
    img.paste(background, (0, img.size[1] - background.size[1]))
    
    start = 50
    for vtb in vtb_videos:
        w, h = font_channel.getsize(vtb[0])
        draw.text(((WIDTH - w) // 2, start), vtb[0], font=font_channel, fill='black')
        start += h

        for video in vtb[-1]:
            start += VIDEO_INT

            title_w, title_h = font_video.getsize(video[0])
            draw.text(((WIDTH - title_w) // 2, start), video[0], font=font_video, fill='black')
            start += title_h + INFO_INT

            while True:
                try:
                    _, content = http.request(video[1]['high']['url'])
                    break
                except:
                    pass
                    
            video_img = Image.open(BytesIO(content))
            img_w, img_h = video_img.size
            img.paste(video_img, ((WIDTH - img_w) // 2, start))
            start += img_h

        start += VTB_INT
    file_path = path.join(path.dirname(__file__), 'cache', f'{str(datetime.now().date())}-{id}.png')
    img.save(file_path)
    print("image saved at " + str(file_path))
    files.append(str(file_path))