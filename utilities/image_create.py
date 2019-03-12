from PIL import Image, ImageDraw, ImageFont
import httplib2
from io import BytesIO
from datetime import datetime
from os import path
import asyncio

http = httplib2.Http(proxy_info = httplib2.ProxyInfo(httplib2.socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080))

async def uploaded_video_img(vtb_videos):
    WIDTH = 1000
    VTB_INT = 30
    VIDEO_INT = 20
    INFO_INT = 10
    VTB_NUM = 5
    async def create_img(vtb_videos, id, files):
        # [[channel_title, thumbnail, [[video1_title, video1_thumbnail], ....], ...]]
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

async def sub_rank_img(rank_list):
    # rank_list [[vtb, subCount], ...] in descending order
    WIDTH = 1000
    LEFT = 30
    RIGHT = 30
    font = ImageFont.truetype(path.join(path.dirname(__file__), 'UDDigiKyokashoN-B.ttc'), 20)
    start = 100
    rank_width = 0
    for id, vtb in enumerate(rank_list):
        id += 1
        rank_size = font.getsize(str(id))
        rank_width = max(rank_width, rank_size[0])
        title_size = font.getsize(vtb[0].channel_title)
        subCount_size = font.getsize(str(vtb[1]))
        thumbnail_size = (88, 88)
        if id <= 20:
            _, h1 = zip(rank_size, title_size, subCount_size, thumbnail_size)
            h1 = max(h1)
            start += 10 + h1
        else:
            _, h2 = zip(rank_size, title_size, subCount_size)
            h2 = max(h2)
            start += 10 + h2

    img = Image.new('RGBA', (WIDTH, start + 100), (254, 248, 232, 255))
    draw = ImageDraw.Draw(img)
    start = 100
    for id, vtb in enumerate(rank_list):
        start += 10
        id += 1
        rank_size = font.getsize(str(id))
        title_size = font.getsize(vtb[0].channel_title)
        subCount_size = font.getsize(str(vtb[1]))
        thumbnail_size = (88, 88)
        if id <= 20:
            _, h = zip(rank_size, title_size, subCount_size, thumbnail_size)
        else:
            _, h = zip(rank_size, title_size, subCount_size)
        h = max(h)

        draw.text((LEFT, start+(h-rank_size[1])//2), str(id), font=font, fill='black')
        if id <= 20:
            while True:
                try:
                    #print(vtb[0].thumbnail_url['default']['url'])
                    _, content = http.request(vtb[0].thumbnail_url['default']['url'])
                    #print("ok!")
                    break
                except:
                    pass
            thumbnail = Image.open(BytesIO(content))
            assert thumbnail.size == thumbnail_size
            img.paste(thumbnail, (LEFT+5+rank_width+5, start+(h-thumbnail_size[1])//2))
        draw.text((LEFT+5+rank_width+5+thumbnail_size[0]+5, start+(h-title_size[1])//2), vtb[0].channel_title, font=font, fill='black')
        draw.text((WIDTH-RIGHT-subCount_size[0], start+(h-subCount_size[1])//2), str(vtb[1]), font=font, fill='black')

        start += h


    file_path = path.join(path.dirname(__file__), 'cache', f'rank.png')
    img.save(file_path)
    print("image saved at " + str(file_path))
    return [str(file_path)]