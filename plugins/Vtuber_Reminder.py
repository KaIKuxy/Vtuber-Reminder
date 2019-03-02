import nonebot
import asyncio
from nonebot import on_command, CommandSession, get_loaded_plugins
from nonebot.permission import SUPERUSER, GROUP
from aiocqhttp.exceptions import Error as CQHttpError
from utilities.youtube import YouTube, youtube
from utilities.channel import database, Vtuber
import httplib2

schedule_checker = dict()
LAZY_CHECK = 2

usage = True

def check_usage():
    global usage
    return usage

@on_command('shutup', aliases=['闭嘴'], permission=SUPERUSER)
async def shutup(session: CommandSession):
    global usage
    usage = False
    await session.send('呜呜呜')

@on_command('speak', aliases=['你可以说话了'], permission=SUPERUSER)
async def speak(session: CommandSession):
    global usage
    usage = True
    await session.send('口球好爽')

@on_command('stream', aliases=['直播'], permission=GROUP)
async def stream(session: CommandSession):
    if not check_usage(): return
    stream_status = await get_stream_status(True)
    print(stream_status)
    await session.send(stream_status)

@nonebot.scheduler.scheduled_job('interval', hours=1)
async def _():
    async def new_video_msg(vtb):
        nonlocal video_status, output, cnt
        if cnt == 10:
            cnt = 0
            if video_status:
                output.append(video_status)
            video_status = ""
        print("checking " + vtb.channel_title + "'s video")
        res = await youtube.newest_video(vtb.video_list_id, vtb.latest_time)
        if len(res[0]) > 0:
            vtb.latest_time = res[1]
            url = thumbnail_msg(vtb.thumbnail_url, 'default')
            msg = f'{vtb.channel_title}{url}:\n'
            for video in res[0]:
                msg += video['title'] + thumbnail_msg(video['thumbnails']) + '\n'
            video_status += msg
        else:
            pass
        cnt += 1
    # check new uploaded video automatically
    print("auto video check")
    bot = nonebot.get_bot()
    video_status = str()
    output = []
    cnt = 0
    tasks = [new_video_msg(vtb) for vtb in database.info()]
    _, _ = await asyncio.wait(tasks)
    try:
        #for vtb in database.info():
            #video_status += await new_video_msg(vtb)
        
        if len(output):
            await bot.send_group_msg(
                group_id=820670085,
                message="新的视频来乐!")
            for status in output:
                await bot.send_group_msg(
                    group_id=820670085,
                    message=status)
            # print(video_status)
            database.store()
            #await bot.send_group_msg(
                #group_id=820670085,
                #message=video_status)
    except CQHttpError:
        print("GROUP MSG ERROR")



@nonebot.scheduler.scheduled_job('interval', minutes=10)
async def _():
    # check ongoing live automatically
    print("auto live check")
    bot = nonebot.get_bot()
    try:
        stream_status = await get_stream_status(False)
        if stream_status:
            # print(stream_status)
            await bot.send_group_msg(
                group_id=820670085,
                message=stream_status)
    except CQHttpError:
        print("GROUP MSG ERROR")

def thumbnail_msg(thumbnail_url: dict(), size=None):
    url = str()
    if size:
        url = thumbnail_url[size]['url']
        pass
    elif 'maxres' in thumbnail_url:
        url = thumbnail_url['maxres']['url']
    elif 'standard' in thumbnail_url:
        url = thumbnail_url['standard']['url']
    elif 'high' in thumbnail_url:
        url = thumbnail_url['high']['url']
    elif 'medium' in thumbnail_url:
        url = thumbnail_url['medium']['url']
    else:
        url = thumbnail_url['default']['url']
    return f'[CQ:image,file={url}]'

async def get_stream_status(mannual: bool) -> str:
    word = ['开播辣!', '正在直播']
    feedback = str()

    async def msg(channel_title, stream_name, thumbnail_url, ch_id, state = mannual):
        #file_path = await youtube.pic_download(url, ch_id)
        #return f'{channel_title} {word[mannual]}: {stream_name}\n[CQ:image,file=file:///{file_path}]\n'
        return f'{channel_title} {word[state]}: {stream_name}\n{thumbnail_msg(thumbnail_url)}\n'
        
    async def check(vtb):
        nonlocal feedback
        print("checking " + vtb.channel_title + "'s live")
        #print(vtb.vtb_id)
        if not mannual: # auto check
            if vtb.vtb_id in schedule_checker and schedule_checker[vtb.vtb_id][0] and schedule_checker[vtb.vtb_id][2] < LAZY_CHECK:
                schedule_checker[vtb.vtb_id][2] += 1
                return 
            stream_status = await youtube.stream_check(vtb.vtb_id)
            if stream_status[0]:
                if ((vtb.vtb_id in schedule_checker and not schedule_checker[vtb.vtb_id][0]) or vtb.vtb_id not in schedule_checker):
                    status = await msg(stream_status[1], stream_status[2], stream_status[3], vtb.vtb_id)
                    feedback += status
                    schedule_checker[vtb.vtb_id] = [True, await msg(stream_status[1], stream_status[2], stream_status[3], vtb.vtb_id, state = True), 0]
                else:
                    schedule_checker[vtb.vtb_id][2] = 0
            else:
                schedule_checker[vtb.vtb_id] = [False]
        else: # mannual check
            if vtb.vtb_id in schedule_checker:
                if schedule_checker[vtb.vtb_id][0] == True:
                    feedback += schedule_checker[vtb.vtb_id][1]
            else:
                stream_status = await youtube.stream_check(vtb.vtb_id)
                if stream_status[0]:
                    status = await msg(stream_status[1], stream_status[2], stream_status[3], vtb.vtb_id)
                    feedback += status
                    schedule_checker[vtb.vtb_id] = [True, await msg(stream_status[1], stream_status[2], stream_status[3], vtb.vtb_id, state = True), 0]
                else:
                    schedule_checker[vtb.vtb_id] = [False]

    global schedule_checker
    tasks = [check(vtb) for vtb in database.info()]
    #for vtb in database.info():
        #await check(vtb)
    _, _ = await asyncio.wait(tasks)
    if mannual and feedback == '':
        feedback = '在我的DD范围里面没有人在直播呢~\n'
    if feedback:
        return feedback[:-1]
    else:
        return feedback


@on_command('ddlist', aliases = ['最新份的DD列表'], permission=GROUP)
async def vtb_info(session: CommandSession):
    if not check_usage(): return
    if len(database.info()) == 0:
        await session.send('我谁都没d')

    async def send_list(vtblist):
        feedback = str()
        for vtb in vtblist:
            url = thumbnail_msg(vtb.thumbnail_url, size='default')
            feedback += f'{vtb.channel_title}{url}\n'
        if len(feedback): feedback = feedback[:-1]
        await session.send(feedback)
    
    id = 0
    while id < len(database.info()):
        await send_list(database.info()[id:min(id + 10, len(database.info()))])
        id += 10
    

@on_command('addchid', permission=SUPERUSER)
async def addchid(session: CommandSession):
    if not check_usage(): return
    ch_id = session.get('ch_id', prompt='你想D谁？倒是告诉我id啊').strip()
    if ch_id:
        add_result = await add_vtb(0, ch_id)
        await session.send(add_result)

@on_command('addname', permission=SUPERUSER)
async def addname(session: CommandSession):
    if not check_usage(): return
    name = session.get('name', prompt='你想D谁？倒是告诉我名字啊').strip()
    if name:
        add_result = await add_vtb(1, name)
        await session.send(add_result)

async def add_vtb(code: int, key: str) -> str:
    # code:
    # 0: add by channel id
    # 1: add by name
    feedback = str()
    if code == 0:
        search_res = await youtube.channel_info(key)
    elif code == 1:
        search_res = await youtube.channel_search(key)
    else:
        search_res = [False]
    # print(search_res)
    if not search_res[0]:
        feedback = '我没有找到有你想看的Vtuber呢~'
    else:
        if database.search(search_res[1]):
            feedback = '你想看的Vtuber已经被我DD辣！'
        else:
            video_list = await youtube.uploaded_video_list(search_res[1])
            vtb = Vtuber(search_res[1], search_res[2], search_res[3], video_list)
            database.add_Vtuber(vtb)
            url = thumbnail_msg(vtb.thumbnail_url, size='default')
            feedback = '你加了ta:\n' + f'{vtb.channel_title}{url}\n'
    return feedback

@addchid.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    #print("stripped_arg_len:")
    #print(len(stripped_arg))
    if session.is_first_run:
        if stripped_arg:
            session.state['ch_id'] = stripped_arg
        return
    if not stripped_arg:
        await session.send('你有病？虚空DD？')
        return 
    session.state[session.current_key] = stripped_arg

@addname.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    #print("stripped_arg_len:")
    #print(len(stripped_arg))
    if session.is_first_run:
        if stripped_arg:
            session.state['name'] = stripped_arg
        return
    if not stripped_arg:
        await session.send('你有病？虚空DD？')
        return 
    session.state[session.current_key] = stripped_arg

@on_command('help', aliases=['帮助', '救救我啊'], permission=GROUP)
async def _(session: CommandSession):
    if not check_usage(): return
    text = r"""
    使用YTB的频道添加Vtuber频道
    addchid [频道id]
    ↑施工中↑

    康康现在有谁在播
    stream/直播

    康康怎么用♂我
    help/帮助/救救我啊
    """
    await session.send(text)
    
    #plugins = list(filter(lambda p: p.name, get_loaded_plugins()))
    #arg = session.current_arg_text.strip().lower()
    #if not arg:
        #await session.send(
            #'大家可以这么用♂我：\n\n' + '\n'.join(p.name for p in plugins))