<<<<<<< HEAD
from nonebot import on_command, CommandSession, get_loaded_plugins
from nonebot.permission import SUPERUSER, GROUP
from utilities.youtube import YouTube
from utilities.channel import database, Vtuber
API_KEY = ''
ADDRESS = None
PORT = None
youtube = YouTube(API_KEY, address=ADDRESS, port=PORT)
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
    stream_status = await get_stream_status()
    await session.send(stream_status)

async def get_stream_status() -> str:
    feedback = str()
    for vtb in database.info():
        #print(vtb.vtb_id)
        stream_status = youtube.stream_check(vtb.vtb_id)
        if stream_status[0] == True:
            feedback += f'{stream_status[1]} 正在直播: {stream_status[2]}\n'
    if feedback == '':
        feedback = '在我的DD范围里面没有人在直播呢~\n'
    return feedback[:-1]


@on_command('add', aliases=['我还想D'], permission=SUPERUSER)
async def add(session: CommandSession):
    ch_id = session.get('ch_id', prompt='你想D谁？倒是告诉我id啊').strip()
    if ch_id:
        add_result = await add_vtb(ch_id)
        await session.send(add_result)

async def add_vtb(ch_id) -> str:
    feedback = str()
    vtb = Vtuber(ch_id)
    database.add_Vtuber(vtb)
    feedback = '好了好了我知道了'
    return feedback

@add.args_parser
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

@on_command('help', aliases=['帮助', '救救我啊'], permission=GROUP)
async def _(session: CommandSession):
    if not check_usage(): return
    text = r"""
    添加想知道的Vtuber频道(限YTB频道)
    add/我还想D [频道id]
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
=======
from nonebot import on_command, CommandSession, get_loaded_plugins
from nonebot.permission import SUPERUSER, GROUP
from utilities.youtube import YouTube
from utilities.channel import database, Vtuber
youtube = YouTube('', address='localhost', port=1080)
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
    stream_status = await get_stream_status()
    await session.send(stream_status)

async def get_stream_status() -> str:
    feedback = str()
    for vtb in database.info():
        #print(vtb.vtb_id)
        stream_status = youtube.stream_check(vtb.vtb_id)
        if stream_status[0] == True:
            feedback += f'{stream_status[1]} 正在直播: {stream_status[2]}\n'
    if feedback == '':
        feedback = '在我的DD范围里面没有人在直播呢~\n'
    return feedback[:-1]


@on_command('add', aliases=['我还想D'], permission=SUPERUSER)
async def add(session: CommandSession):
    ch_id = session.get('ch_id', prompt='你想D谁？倒是告诉我id啊').strip()
    if ch_id:
        add_result = await add_vtb(ch_id)
        await session.send(add_result)

async def add_vtb(ch_id) -> str:
    feedback = str()
    vtb = Vtuber(ch_id)
    database.add_Vtuber(vtb)
    feedback = '好了好了我知道了'
    return feedback

@add.args_parser
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

@on_command('help', aliases=['帮助', '救救我啊'], permission=GROUP)
async def _(session: CommandSession):
    if not check_usage(): return
    text = r"""
    添加想知道的Vtuber频道(限YTB频道)
    add/我还想D [频道id]
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
>>>>>>> update
        #return