import re
from asyncio import TimeoutError

from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER, GROUP_ADMIN
from nonebot.params import RawCommand
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from .config import Config
from .mediawiki import MediaWiki, MediaWikiAPIURLError
from .utilities import process_command

QUIT_LIST = ["取消", "quit", "退出", "exit", "算了"]
BotConfig = get_driver().config
reserved = ["talk", "user", "user talk", "project", "project talk", "file", "file talk", "mediawiki",
            "mediawiki talk", "template", "template talk", "help", "help talk", "category", "category talk",
            "special", "media", "t", "u"]

add_wiki = on_command("wiki.add", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@add_wiki.handle()
async def _add_wiki(bot: Bot, event: MessageEvent, raw_command: str = RawCommand()):
    msg = str(event.message).strip()
    param_list, param_dict = process_command(raw_command, msg)

    # check if is global
    is_global = False
    if param_dict.get("g"):
        if await SUPERUSER(bot, event):
            is_global = True
        else:
            await add_wiki.finish("您没有权限使用此命令！")

    # parse params
    if len(param_list) <= 1:
        await add_wiki.finish("请输入正确的参数！格式为： wiki.add <前缀> <API地址（可选）> <条目路径> < -g （添加该参数修改全局）>")
        return  # 糊弄下IDE
    elif len(param_list) == 2:
        prefix = param_list[0].strip().lower()
        api = ''
        url = param_list[1].strip().rstrip('/')  # 防止之后拼接的时候多出来斜杠
    else:
        prefix = param_list[0].strip().lower()
        api = param_list[1].strip().rstrip('/')
        url = param_list[2].strip().rstrip('/')

    # check params
    if url.endswith('api.php'):
        await add_wiki.finish("参数错误！如果您只提供了一个地址，则其必须是条目路径而非api地址")
    if api and not re.match(r'^https?:/{2}\w.+$', api):
        await add_wiki.finish("非法的api地址，请重新输入！")
    if not re.match(r'^https?:/{2}\w.+$', url):
        await add_wiki.finish("非法的条目路径，请重新输入！")
    if prefix in reserved or ":" in prefix or "：" in prefix:
        await add_wiki.finish("该前缀为保留前缀或含有非法字符，请重新输入！")

    if api:
        success = False
        for i in range(3):
            try:
                await MediaWiki.create(url=api, timeout=10)
                success = True
                break
            except (MediaWikiAPIURLError, TimeoutError):
                continue
        if not success:
            await add_wiki.finish("无法连接到wiki，请检查api地址是否正确！如果确认无误，可能是网络故障或者防火墙拦截，"
                                  "您可以不提供api地址，直接提供条目路径即可")

    # 进行插入操作
    group_id = event.group_id if isinstance(event, GroupMessageEvent) else 0
    config = Config(group_id=group_id)
    if (is_global and config.add_wiki_global(prefix, api, url)) \
            or (not is_global and config.add_wiki(prefix, api, url)):
        await add_wiki.finish(f"添加/编辑Wiki：{prefix}成功！")
    else:
        await add_wiki.finish("呜……出错了……请联系bot管理员进行处理……")


list_wiki = on_command("wiki.list")


@list_wiki.handle()
async def _list_wiki(bot: Bot, event: MessageEvent, raw_command: str = RawCommand()):
    msg = str(event.message).strip()
    param_list, param_dict = process_command(raw_command, msg)

    # check if is global
    is_global = bool(param_dict.get("g"))

    if is_global:
        config = Config(group_id=0)
        await list_wiki.finish(config.list_data[1])
    elif isinstance(event, GroupMessageEvent):
        config = Config(group_id=event.group_id)
        await list_wiki.finish(config.list_data[0])


del_wiki = on_command("wiki.delete", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@del_wiki.handle()
async def _del_wiki(bot: Bot, event: MessageEvent, raw_command: str = RawCommand()):
    msg = str(event.message).strip()
    param_list, param_dict = process_command(raw_command, msg)

    # check if is global
    is_global = False
    if param_dict.get("g"):
        if await SUPERUSER(bot, event):
            is_global = True
        else:
            await del_wiki.finish("您没有权限使用此命令！")

    if not param_list:
        await del_wiki.finish("你似乎没有提供要删除的前缀的说……")
    prefix = param_list[0]
    group_id = event.group_id if isinstance(event, GroupMessageEvent) else 0
    config = Config(group_id=group_id)

    if (is_global and config.del_wiki_global(prefix)) or (not is_global and config.del_wiki(prefix)):
        await del_wiki.finish("删除成功")
    else:
        await del_wiki.finish("呜……删除失败了……请检查前缀是否有误")


set_default = on_command("wiki.default", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@set_default.handle()
async def _set_default(bot: Bot, event: MessageEvent, state: T_State, raw_command: str = RawCommand()):
    msg = str(event.message).strip()
    param_list, param_dict = process_command(raw_command, msg)

    # check if is global
    is_global = False
    if param_dict.get("g"):
        if await SUPERUSER(bot, event):
            is_global = True
        else:
            await set_default.finish("您没有权限使用此命令！")

    if not param_list:
        await set_default.finish("你似乎没有提供要设置的前缀的说……")
    prefix = param_list[0]
    group_id = event.group_id if isinstance(event, GroupMessageEvent) else 0
    config = Config(group_id=group_id)

    if (is_global and config.set_default_global(prefix)) or (not is_global and config.set_default(prefix)):
        await set_default.finish("设置成功")
    else:
        await set_default.finish("呜……设置失败了……请检查前缀是否有误")
