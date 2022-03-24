from typing import Union
from urllib import parse

import nonebot
from aiohttp.client_exceptions import ContentTypeError

from .mwapi import Mwapi
from .exception import MediaWikiException, MediaWikiGeoCoordError, HTTPTimeoutError, PageError


class Wiki:
    def __init__(self, api_url: str, fallback_url: str):
        self.__url = fallback_url
        self.__api_url = api_url

    async def get_from_api(self, title: str, is_template: bool) -> tuple[bool, Union[str, list]]:
        """第一个值表示是否为特殊类型（目前是列表选择），第二个是查询结果（正常情况是字符串，特殊情况是列表）"""
        if is_template:
            title = "Template:" + title
        if self.__api_url == '':
            title, anchor = Mwapi.handle_anchor_pre_process(title)
            special, url = await self.url_parse(title)
            url = Mwapi.handle_anchor_post_process(url, anchor)
            result = f"标题：{title}\n链接：{url}"
            return False, result

        try:
            mediawiki = Mwapi(url=self.__url, api_url=self.__api_url)
            result_dict = await mediawiki.get_page_info(title)
        except HTTPTimeoutError:
            exception = "连接超时"
        except (MediaWikiException, MediaWikiGeoCoordError, ContentTypeError) as e:
            exception = "Api调用出错"
            nonebot.logger.warning(e)
        except PageError:
            exception = "未找到页面"
        if "exception" in locals():
            special, result = await self.url_parse(title)
            result_dict = {
                "exception": True,
                "title": title,
                "url": result,
                "notes": exception,
            }

        if result_dict["exception"]:
            result = f"错误：{result_dict['notes']}\n" \
                     f"由条目名直接生成的链接：\n" \
                     f"标题：{result_dict['title']}\n链接：{result_dict['url']}"
            return False, result
        if result_dict["interwiki"]:
            result = f"跨wiki链接：{result_dict['title']}\n" \
                     f"链接：{result_dict['url']}"
            return False, result
        if result_dict["missing"] or result_dict["disambiguation"]:
            result = result_dict["notes"]
            result.append((result_dict["missing"], result_dict["title"]))  # 最后一个值保存是缺失还是重定向，以及目标页面标题
            return True, result
        if result_dict["redirected"]:
            result = f"重定向：{result_dict['from_title']} → {result_dict['title']}\n" \
                     f"链接：{result_dict['url']}"
            return False, result

        result = f"标题：{result_dict['title']}\n链接：{result_dict['url']}"
        return False, result

    async def url_parse(self, title: str) -> tuple:
        result = f"{self.__url}/{parse.quote(title)}"
        return False, result
