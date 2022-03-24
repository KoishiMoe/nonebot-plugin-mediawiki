import re

from nonebot import Type
from nonebot.adapters.onebot.v11 import Bot, utils, GroupMessageEvent, Message
from nonebot.internal.matcher import Matcher

from .config import Config
from .data_source import Wiki
from .exception import NoDefaultPrefixException, NoSuchPrefixException

__all__ = ['wiki_process', 'wiki_parse']

# 匹配模板
ARTICLE = r"\[\[(.*?)\]\]"
TEMPLATE = r"\{\{(.*?)\}\}"

# 标题列表
titles = []


async def wiki_process(bot: Bot, event: GroupMessageEvent, wiki: Type[Matcher], is_template: bool = False):
    global titles
    message = str(event.message).strip()
    if message.isdigit():
        if 0 <= int(message) < len(titles) - 1:
            event.message = Message(f"[[{titles[-1]}:{titles[int(message)]}]]")
            is_template = False  # 否则会导致下面发生误判，导致无法匹配
        else:
            return
    special, result = await wiki_parse(ARTICLE if not is_template else TEMPLATE, is_template, False, bot, event)
    if special:
        titles = result[:-1]
        titles.insert(0, result[-1][1])
        titles.append(result[-1][2])
        title_list = '\n'.join([f'{i + 1}.{result[i]}' for i in range(len(result) - 1)])  # 最后一个元素是特殊标记
        msg = f"{f'页面“{result[-1][1]}”不存在，下面是推荐的结果' if result[-1][0] else f'页面{result[-1][1]}是消歧义页面'}，" \
              f"请回复数字来选择你想要查询的条目，或者回复0来根据原标题直接生成链接：\n" \
              f"{title_list}"
        await wiki.reject(msg)
    else:
        await bot.send(event, result)
        titles = []


async def wiki_parse(pattern: str, is_template: bool, is_raw: bool, bot: Bot, event: GroupMessageEvent) -> tuple:
    msg = str(event.message).strip()
    msg = utils.unescape(msg)  # 将消息处理为正常格式，以防搜索出错
    temp_config: Config = Config(event.group_id)
    titles = re.findall(pattern, msg)
    for title in titles:
        title = str(title)
        prefix = re.match(r'\w+:|\w+：', title)
        if not prefix:
            prefix = ''
        else:
            prefix = prefix.group(0).lower().rstrip(":：")  # 删掉右侧冒号以进行匹配
            if prefix in temp_config.prefixes:
                title = re.sub(f"{prefix}:|{prefix}：", '', title, count=1, flags=re.I)  # 去除标题左侧的前缀
            else:
                prefix = ''  # 如果不在前缀列表里，视为名字空间标识，回落到默认前缀

        try:
            if title is None or title.strip() == "":
                continue
            wiki_api = temp_config.get_from_prefix(prefix)[0]
            wiki_url = temp_config.get_from_prefix(prefix)[1]

            wiki_object = Wiki(wiki_api, wiki_url)
            if not is_raw:
                special, result = await wiki_object.get_from_api(title, is_template)
            else:
                special, url = await wiki_object.url_parse(title)
                result = f"标题：{title}\n链接：{url}"

            if special:
                result[-1] = list(result[-1])
                result[-1].append(prefix)  # 补充前缀，防止一会查的时候回落到默认wiki

        except NoDefaultPrefixException:
            special = False
            result = "没有找到默认前缀，请群管或bot管理员先设置默认前缀"
        except NoSuchPrefixException:
            special = False
            result = "指定的默认前缀对应的wiki不存在，请管理员检查设置"

        return special, result
