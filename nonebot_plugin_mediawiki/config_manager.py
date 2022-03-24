import re
from typing import Type

from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Event, Message
from nonebot.adapters.onebot.v11.permission import GROUP_OWNER, GROUP_ADMIN, GROUP  # , PRIVATE
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

from .config import Config
from .mwapi import Mwapi

'''
设置管理器部分大量借(chao)鉴(xi)了 nonebot-hk-reporter 插件（以MIT许可证授权）的源码
Github地址：https://github.com/felinae98/nonebot-hk-reporter
协议：https://github.com/felinae98/nonebot-hk-reporter/blob/main/LICENSE
'''


def _gen_prompt_template(prompt: str):
    if hasattr(Message, 'template'):
        return Message.template(prompt)
    return prompt


def do_add_wiki(add_wiki: Type[Matcher]):
    @add_wiki.handle()
    async def init_promote(state: T_State):
        await init_promote_public(state)

    async def parse_prefix(event: Event, state: T_State) -> None:
        await parse_prefix_public(add_wiki, event, state)

    @add_wiki.got('prefix', _gen_prompt_template('{_prompt}'), [Depends(parse_prefix)])
    @add_wiki.handle()
    async def init_api_url(state: T_State):
        await init_api_url_public(state)

    async def parse_api_url(event: Event, state: T_State):
        await parse_api_url_public(add_wiki, event, state)

    @add_wiki.got('api_url', _gen_prompt_template('{_prompt}'), [Depends(parse_api_url)])
    @add_wiki.handle()
    async def init_url(state: T_State):
        await init_url_public(state)

    async def parse_url(event: Event, state: T_State):
        await parse_url_public(add_wiki, event, state)

    @add_wiki.got('url', _gen_prompt_template('{_prompt}'), [Depends(parse_url)])
    @add_wiki.handle()
    async def add_wiki_process(event: GroupMessageEvent, state: T_State):
        await add_wiki_all_process_public(event.group_id, add_wiki, state)


def do_query_wikis(query_wikis: Type[Matcher]):
    @query_wikis.handle()
    async def _(event: GroupMessageEvent):
        await __public(event.group_id, query_wikis)


def do_del_wiki(del_wiki: Type[Matcher]):
    @del_wiki.handle()
    async def send_list(event: GroupMessageEvent):
        await send_list_public(event.group_id, del_wiki)

    @del_wiki.receive()
    async def do_del(event: GroupMessageEvent):
        await do_del_public(event.group_id, del_wiki, event)


def do_set_default(set_default: Type[Matcher]):
    @set_default.handle()
    async def send_list(event: GroupMessageEvent):
        await send_list_public(event.group_id, set_default)

    @set_default.receive()
    async def do_set(event: GroupMessageEvent):
        await do_set_public(event.group_id, set_default, event)


# 全局wiki设置

def do_add_wiki_global(add_wiki_global: Type[Matcher]):
    @add_wiki_global.handle()
    async def init_promote(state: T_State):
        await init_promote_public(state)

    async def parse_prefix(event: Event, state: T_State) -> None:
        await parse_prefix_public(add_wiki_global, event, state)

    @add_wiki_global.got('prefix', _gen_prompt_template('{_prompt}'), [Depends(parse_prefix)])
    @add_wiki_global.handle()
    async def init_api_url(state: T_State):
        await init_api_url_public(state)

    async def parse_api_url(event: Event, state: T_State):
        await parse_api_url_public(add_wiki_global, event, state)

    @add_wiki_global.got('api_url', _gen_prompt_template('{_prompt}'), [Depends(parse_api_url)])
    @add_wiki_global.handle()
    async def init_url(state: T_State):
        await init_url_public(state)

    async def parse_url(event: Event, state: T_State):
        await parse_url_public(add_wiki_global, event, state)

    @add_wiki_global.got('url', _gen_prompt_template('{_prompt}'), [Depends(parse_url)])
    @add_wiki_global.handle()
    async def add_wiki_global_process(state: T_State):
        await add_wiki_all_process_public(0, add_wiki_global, state)


def do_query_wikis_global(query_wikis_global: Type[Matcher]):
    @query_wikis_global.handle()
    async def _():
        await __public(0, query_wikis_global)


def do_del_wiki_global(del_wiki_global: Type[Matcher]):
    @del_wiki_global.handle()
    async def send_list():
        await send_list_public(0, del_wiki_global)

    @del_wiki_global.receive()
    async def do_del(event: Event):
        await do_del_public(0, del_wiki_global, event)


def do_set_default_global(set_default_global: Type[Matcher]):
    @set_default_global.handle()
    async def send_list():
        await send_list_public(0, set_default_global)

    @set_default_global.receive()
    async def do_set(event: Event):
        await do_set_public(0, set_default_global, event)


# 公用函数

async def init_promote_public(state: T_State):
    state['_prompt'] = "请回复前缀（仅用于标识），回复“取消”以中止："


async def parse_prefix_public(parameter: Type[Matcher], event: Event, state: T_State) -> None:
    prefix = str(event.get_message()).strip().lower()
    reserved = ["(main)", "talk", "user", "user talk", "project", "project talk", "file", "file talk", "mediawiki",
                "mediawiki talk", "template", "template talk", "help", "help talk", "category", "category talk",
                "special", "media", "t", "u"]
    if prefix == "取消":
        await parameter.finish("OK")
    elif prefix in reserved:
        await parameter.reject("前缀位于保留名字空间！请重新输入！")
    elif re.findall(r'\W', prefix):
        await parameter.reject("前缀含有非法字符，请重新输入！")
    else:
        state['prefix'] = prefix


async def init_api_url_public(state: T_State):
    state['_prompt'] = "请输入wiki的api地址，回复“0”跳过"


async def parse_api_url_public(parameter: Type[Matcher], event: Event, state: T_State):
    api_url = str(event.get_message()).strip()
    if api_url.lower() == '0':
        state['api_url'] = ''
    elif api_url == '取消':
        await parameter.finish("OK")
    elif not re.match(r'^https?:/{2}\w.+$', api_url):
        await parameter.reject("非法url!请重新输入！")
    else:
        api = Mwapi(url='', api_url=api_url)
        if not await api.test_api():
            await parameter.reject("无法连接到api，请重新输入！如果确认无误的话，可能是被防火墙拦截，可以回复“0”跳过，或者“取消”来退出")
        state['api_url'] = api_url.strip().rstrip("/")


async def init_url_public(state: T_State):
    state['_prompt'] = '请输入wiki的通用url（必填）'


async def parse_url_public(parameter: Type[Matcher], event: Event, state: T_State):
    url = str(event.get_message()).strip()
    if url == "取消":
        await parameter.finish("OK")
    elif not re.match(r'^https?:/{2}\w.+$', url):
        await parameter.reject("非法url！请重新输入！")
    else:
        state['url'] = url.strip().rstrip("/")


async def add_wiki_all_process_public(group_id: int, parameter: Type[Matcher], state: T_State):
    config: Config = Config(group_id)
    prefix: str = state["prefix"]
    api_url: str = state["api_url"]
    url: str = state["url"]
    if group_id == 0 and config.add_wiki_global(prefix, api_url, url):
        await parameter.finish(f"添加/编辑Wiki: {prefix} 成功！")
    elif config.add_wiki(prefix, api_url, url):
        await parameter.finish(f"添加/编辑Wiki: {prefix} 成功！")
    else:
        await parameter.finish("呜……出错了……如果持续出现，请联系bot管理员进行排查")


async def __public(group_id: int, parameter: Type[Matcher]):
    config: Config = Config(group_id)
    all_data: tuple = config.list_data
    all_data_str: str = all_data[1] if group_id == 0 else all_data[0] + all_data[1]
    await parameter.finish(all_data_str)


async def send_list_public(group_id: int, parameter: Type[Matcher]):
    config: Config = Config(group_id)
    tmp_str = "全局" if group_id == 0 else "本群"
    res = f"以下为{tmp_str}绑定的所有wiki列表，请回复前缀来选择wiki，回复“取消”退出：\n"
    res += config.list_data[1] if group_id == 0 else config.list_data[0]
    await parameter.send(message=Message(res))


async def do_del_public(group_id: int, parameter: Type[Matcher], event: Event):
    prefix = str(event.get_message()).strip()
    if prefix == "取消":
        await parameter.finish("OK")
    else:
        config: Config = Config(group_id)
        if group_id == 0 and config.del_wiki_global(prefix):
            await parameter.finish("删除成功")
        elif config.del_wiki(prefix):
            await parameter.finish("删除成功")
        else:
            await parameter.finish("删除失败……请检查前缀是否有误")


async def do_set_public(group_id: int, parameter: Type[Matcher], event: Event):
    prefix = str(event.get_message()).strip()
    if prefix == "取消":
        await parameter.finish("OK")
    else:
        config: Config = Config(group_id)
        if group_id == 0 and config.set_default_global(prefix):
            await parameter.finish("设置成功")
        elif config.set_default(prefix):
            await parameter.finish("设置成功")
        else:
            await parameter.finish("设置失败……请检查前缀是否有误")


# Matchers

add_wiki_matcher = on_command("wiki.add", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
do_add_wiki(add_wiki_matcher)
add_wiki_global_matcher = on_command("wiki.add.global", permission=SUPERUSER)
do_add_wiki_global(add_wiki_global_matcher)

query_wikis_matcher = on_command("wiki.list", permission=GROUP)
do_query_wikis(query_wikis_matcher)
query_wikis_global_matcher = on_command("wiki.list.global")
do_query_wikis_global(query_wikis_global_matcher)

del_wiki_matcher = on_command("wiki.delete", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
do_del_wiki(del_wiki_matcher)
del_wiki_global_matcher = on_command("wiki.delete.global", permission=SUPERUSER)
do_del_wiki_global(del_wiki_global_matcher)

set_default_matcher = on_command("wiki.default", permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER)
do_set_default(set_default_matcher)
set_default_global_matcher = on_command("wiki.default.global", permission=SUPERUSER)
do_set_default_global(set_default_global_matcher)
