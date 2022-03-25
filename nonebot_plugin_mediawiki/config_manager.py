import re
from typing import Type

from nonebot import on_command, get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, MessageEvent
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER, GROUP_ADMIN
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.internal.matcher import Matcher

from .config import Config
from .mwapi import Mwapi

QUIT_LIST = ["取消", "quit", "退出"]
BotConfig = get_driver().config

add_wiki = on_command("wiki.add", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@add_wiki.handle()
async def _add_wiki(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.message).strip().removeprefix("wiki.add")
    state["global"] = msg == ".global"

    if state["global"] and str(event.user_id) not in BotConfig.superusers:
        await add_wiki.finish()


@add_wiki.got("prefix", "请回复前缀，或回复“取消”以退出")
async def _add_wiki_prefix(bot: Bot, event: MessageEvent, state: T_State):
    prefix = str(state["prefix"]).strip().lower()
    reserved = ["talk", "user", "user talk", "project", "project talk", "file", "file talk", "mediawiki",
                "mediawiki talk", "template", "template talk", "help", "help talk", "category", "category talk",
                "special", "media", "t", "u"]

    if prefix in QUIT_LIST:
        await add_wiki.finish("OK")
    elif prefix in reserved:
        await add_wiki.reject("前缀位于保留名字空间！请重新输入！")
    elif re.findall(r'\W', prefix):
        await add_wiki.reject("前缀含有非法字符，请重新输入！")
    else:
        state['prefix'] = prefix


@add_wiki.got("api_url", "请输入wiki的api地址，回复“0”跳过")
async def _add_wiki_api_url(bot: Bot, event: MessageEvent, state: T_State):
    api_url = str(state["api_url"]).strip()

    if api_url == "0":
        state["api_url"] = ''
    elif api_url in QUIT_LIST:
        await add_wiki.finish("OK")
    elif not re.match(r'^https?:/{2}\w.+$', api_url):
        await add_wiki.reject("非法url!请重新输入！")
    else:
        api = Mwapi(url='', api_url=api_url)
        if not await api.test_api():
            await add_wiki.reject("无法连接到api，请重新输入！如果确认无误的话，可能是被防火墙拦截，可以回复“0”跳过，或者“取消”来退出")
        state['api_url'] = api_url.strip().rstrip("/")  # 之所以去掉右边的斜杠，是为了防止之后需要进行拼接等操作时因多出来斜杠而出错


@add_wiki.got("url", "请输入wiki的通用url（必填）")
async def _add_wiki_url(bot: Bot, event: MessageEvent, state: T_State):
    url = str(state["url"]).strip()

    if url in QUIT_LIST:
        await add_wiki.finish("OK")
    elif not re.match(r'^https?:/{2}\w.+$', url):
        await add_wiki.reject("非法url！请重新输入！")
    else:
        state['url'] = url.strip().rstrip("/")

    # 进行插入操作
    group_id = event.group_id if isinstance(event, GroupMessageEvent) else 0
    config = Config(group_id=group_id)
    if (state["global"] and config.add_wiki_global(state["prefix"], state["api_url"], state["url"])) \
            or (not state["global"] and config.add_wiki(state["prefix"], state["api_url"], state["url"])):
        await add_wiki.finish(f"添加/编辑Wiki：{state['prefix']}成功！")
    else:
        await add_wiki.finish("呜……出错了……请联系bot管理员进行处理……")


list_wiki = on_command("wiki.list")

@list_wiki.handle()
async def _list_wiki(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.message).strip().removeprefix("wiki.list")
    is_global = msg == ".global"

    if is_global:
        config = Config(group_id=0)
        await list_wiki.finish(config.list_data[1])
    elif isinstance(event, GroupMessageEvent):
        config = Config(group_id=event.group_id)
        await list_wiki.finish(config.list_data[0])


del_wiki = on_command("wiki.delete", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@del_wiki.handle()
async def _del_wiki(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.message).strip().removeprefix("wiki.delete")

    await __check_params(msg=msg, event=event, state=state, matcher=del_wiki)


@del_wiki.got("prefix", "请回复前缀，或回复“取消”以退出")
async def _del_wiki_prefix(bot: Bot, event: MessageEvent, state: T_State):
    prefix, config = await __check_prefix(event=event, state=state, matcher=del_wiki)

    if (state["global"] and config.del_wiki_global(prefix)) or (not state["global"] and config.del_wiki(prefix)):
        await del_wiki.finish("删除成功")
    else:
        await del_wiki.finish("呜……删除失败了……请检查前缀是否有误")


set_default = on_command("wiki.default", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)


@set_default.handle()
async def _set_default(bot: Bot, event: MessageEvent, state: T_State):
    msg = str(event.message).strip().removeprefix("wiki.default")

    await __check_params(msg=msg, event=event, state=state, matcher=set_default)


@set_default.got("prefix", "请输入要设置的前缀，或者回复“取消”退出")
async def set_default_prefix(bot: Bot, event: MessageEvent, state: T_State):
    prefix, config = await __check_prefix(event=event, state=state, matcher=set_default)

    if (state["global"] and config.set_default_global(prefix)) or (not state["global"] and config.set_default(prefix)):
        await del_wiki.finish("设置成功")
    else:
        await del_wiki.finish("呜……设置失败了……请检查前缀是否有误")


# 一些公用的部分
async def __check_params(msg: str, event: MessageEvent, state: T_State, matcher: Type[Matcher]):
    params_list = msg.split(maxsplit=1)

    state["global"] = params_list[0] == ".global" if params_list else False
    if len(params_list) == 2 and state["global"]:
        state["prefix"] = params_list[1]
    elif params_list:
        state["prefix"] = params_list[0]

    if state["global"] and str(event.user_id) not in BotConfig.superusers:
        await matcher.finish()


async def __check_prefix(event: MessageEvent, state: T_State, matcher: Type[Matcher]) -> tuple[str, Config]:
    prefix = str(state['prefix']).strip()
    state['prefix'] = prefix

    if prefix in QUIT_LIST:
        await matcher.finish("OK")
    elif re.findall(r'\W', prefix):
        await matcher.reject("前缀含有非法字符，请重新输入！")

    group_id = event.group_id if isinstance(event, GroupMessageEvent) else 0
    config = Config(group_id=group_id)

    return prefix, config
