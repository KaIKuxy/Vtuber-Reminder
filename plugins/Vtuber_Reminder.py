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
        stream_status = await youtube.stream_check(vtb.vtb_id)
        if stream_status[0] == True:
            feedback += f'{stream_status[1]} 正在直播: {stream_status[2]}\n'
    if feedback == '':
        feedback = '在我的DD范围里面没有人在直播呢~\n'
    return feedback[:-1]


@on_command('ddlist', aliases = ['最新份的DD列表'], permission=GROUP)
async def vtb_info(session: CommandSession):
    feedback = str()
    if not check_usage(): return
    for vtb in database.info():
        feedback += vtb.channel_title + '\n'
    if len(feedback): feedback = feedback[:-1]
    await session.send(feedback)

@on_command('addchid', permission=SUPERUSER)
async def addchid(session: CommandSession):
    ch_id = session.get('ch_id', prompt='你想D谁？倒是告诉我id啊').strip()
    if ch_id:
        add_result = await add_vtb(0, ch_id)
        await session.send(add_result)

@on_command('addname', permission=SUPERUSER)
async def addname(session: CommandSession):
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
    print(search_res)
    if not search_res[0]:
        feedback = '我没有找到有你想看的Vtuber呢~'
    else:
        if database.search(search_res[1]):
            feedback = '你想看的Vtuber已经被我DD辣！'
        else:
            vtb = Vtuber(search_res[1], search_res[2], search_res[3])
            database.add_Vtuber(vtb)
            feedback = '你加了ta:\n' + search_res[2]
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