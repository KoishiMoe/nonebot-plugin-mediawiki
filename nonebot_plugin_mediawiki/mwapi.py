import re
from asyncio.exceptions import TimeoutError
from re import compile
from typing import Optional, Union
from urllib import parse

import aiohttp
from nonebot.log import logger

from .exception import HTTPTimeoutError, MediaWikiException, MediaWikiGeoCoordError, PageError

'''
代码主要来自 pymediawiki 库（以MIT许可证开源），并根据bot的实际需要做了一些修改
该库的Github地址：https://github.com/barrust/mediawiki
许可证：https://github.com/barrust/mediawiki/blob/master/LICENSE
'''

USER_AGENT: str = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
ODD_ERROR_MESSAGE = (
    "出现了未知问题……如果您所查询的目标wiki以及目标条目均正常，那么可能是bot出现了bug,"
    "请在项目的github页面上提交issue,并附上您查询的目标wiki、条目名及bot日志（若有）"
)
ClientTimeout = aiohttp.ClientTimeout


class Mwapi:
    def __init__(self, url: str, api_url: str = '', ua: str = USER_AGENT,
                 timeout: ClientTimeout = ClientTimeout(total=30)):
        self._api_url = api_url
        self._url = url
        self._timeout = timeout
        self._ua = ua
        self._title = None
        self._page_url = None
        self._redirected = False
        self._disambiguation = False
        self._missing = False
        self._interwiki = False
        self._from_title = None
        self._pageid = None
        self._anchor = None

    async def _wiki_request(self, params: dict) -> dict:
        # update params
        params["format"] = "json"
        if "action" not in params:
            params["action"] = "query"

        session = aiohttp.ClientSession()
        headers = {"User-Agent": self._ua}

        # get response
        try:
            resp = await session.get(self._api_url, params=params, headers=headers, timeout=self._timeout)
        except TimeoutError:
            await session.close()
            raise HTTPTimeoutError(query='')
        resp_dict = await resp.json()

        await session.close()

        return resp_dict

    async def _wikitext(self) -> str:
        query_params = {
            "action": "parse",
            "page": self._title,
            "prop": "wikitext",
            "formatversion": 2,
        }
        request = await self._wiki_request(query_params)

        # 是消歧义页的前提是页面存在，所以这里不做检测了（
        return request["parse"]["wikitext"]

    @staticmethod
    def _check_error_response(response, query):
        """ check for default error messages and throw correct exception """
        if "error" in response:
            http_error = ["HTTP request timed out.", "Pool queue is full"]
            geo_error = [
                "Page coordinates unknown.",
                "One of the parameters gscoord, gspage, gsbbox is required",
                "Invalid coordinate provided",
            ]
            err = response["error"]["info"]
            if err in http_error:
                raise HTTPTimeoutError(query)
            if err in geo_error:
                raise MediaWikiGeoCoordError(err)
            raise MediaWikiException(err)

    async def test_api(self) -> bool:
        try:
            params = {"meta": "siteinfo", "siprop": "extensions|general"}
            resp = await self._wiki_request(params)
        except Exception as e:
            logger.info(f"测试wiki api时出现了错误：{e}")
            return False

        query = resp.get("query", None)
        if query is None or query.get("general", None) is None:
            return False

        return True

    async def search(self, query: str, results: int = 10, suggestion: bool = False) -> Union[tuple, list]:

        max_pull = 500  # api有500的上限

        search_params = {
            "list": "search",
            "srprop": "",
            "srlimit": min(results, max_pull) if results is not None else max_pull,
            "srsearch": query,
            "sroffset": 0,  # this is what will be used to pull more than the max
        }
        if suggestion:
            search_params["srinfo"] = "suggestion"

        raw_results = await self._wiki_request(search_params)

        self._check_error_response(raw_results, query)

        search_results = [d["title"] for d in raw_results["query"]["search"]]

        if suggestion:
            sug = None
            if raw_results["query"].get("searchinfo"):
                sug = raw_results["query"]["searchinfo"]["suggestion"]
            return search_results, sug
        return search_results

    async def suggest(self, query) -> Optional[str]:
        res, suggest = await self.search(query, results=1, suggestion=True)
        try:
            title = res[0] or suggest
        except IndexError:  # page doesn't exist
            title = None
        return title

    async def opensearch(self, query, results=10, redirect=True):
        max_pull = 500

        query_params = {
            "action": "opensearch",
            "search": query,
            "limit": (min(results, max_pull) if results is not None else max_pull),
            "redirects": ("resolve" if redirect else "return"),
            "warningsaserror": True,
            "namespace": "",
        }

        results = await self._wiki_request(query_params)

        self._check_error_response(results, query)

        res = []
        for i, item in enumerate(results[1]):
            res.append((item, results[2][i], results[3][i]))
        return res

    async def get_page_info(self, title: str, redirect: bool = True) -> dict:
        title, anchor = self.handle_anchor_pre_process(title)
        self._title = title
        self._anchor = anchor if anchor else self._anchor  # 有新的锚点就替换掉旧的

        query_params = {
            "titles": self._title,
            "prop": "info|pageprops",
            "inprop": "url",
            "ppprop": "disambiguation",
            "converttitles": 1,
            "iwurl": 1,
        }
        if redirect:
            query_params["redirects"] = 1

        request = await self._wiki_request(query_params)

        self._check_error_response(request, title)

        query = request["query"]
        if query.get("pages", None):
            pageid = list(query["pages"].keys())[0]
            page = query["pages"][pageid]
            self._pageid = pageid

        # determine result of the request
        # redirects is present in query if page is a redirect
        # 有重定向的情况下，query中没有'pages'，所以把重定向检测放在前面
        if "redirects" in query:
            await self._handle_redirect(query=query)
        # 同理，处理跨wiki
        if "interwiki" in query:
            await self._handle_interwiki(query=query)
        # missing is present if the page is missing
        elif "missing" in page or pageid == '-1':
            search_list = await self._handle_missing_page()
        # if pageprops is returned, it must be a disambiguation error
        elif "pageprops" in page:
            self._disambiguation = True
            self._page_url = page["fullurl"]
            self._title = page["title"]
            found_list = await self._handle_disambiguation()
        else:
            self._page_url = page["fullurl"]

        # 使用curid以缩短链接
        # 不确定兼容性，如有问题请至项目github页面提交issue
        # 按理说api.php应该和index.php在一起的吧……应该吧……
        if self._pageid and not self._interwiki:
            self._page_url = f"{self._api_url.removesuffix('api.php')}index.php?curid={self._pageid}"

        self._page_url = self.handle_anchor_post_process(url=self._page_url, anchor=self._anchor)

        result = {
            "exception": False,
            "redirected": self._redirected,
            "disambiguation": self._disambiguation,
            "missing": self._missing,
            "interwiki": self._interwiki,
            "title": self._title,
            "url": self._page_url,
            "from_title": self._from_title,
            "notes": found_list if self._disambiguation else search_list if self._missing else ''
        }

        return result

    async def _handle_redirect(self, query):
        """ handle redirect """

        final_redirect = query["redirects"][-1]

        if "normalized" in query:
            normalized = query["normalized"][0]
            if normalized["from"] != self._title:
                raise MediaWikiException(ODD_ERROR_MESSAGE)
            from_title = normalized["to"]
        else:
            from_title = self._title

        if not from_title == final_redirect["to"]:  # 循环重定向
            await self.get_page_info(final_redirect["to"], redirect=False)  # 虽然前面已经检测过循环重定向了，不过以防万一
        else:
            await self.get_page_info(final_redirect["from"], redirect=False)  # 防止绕回来
        self._from_title = from_title
        self._redirected = True

    async def _handle_interwiki(self, query):
        inter_wiki = query["interwiki"][0]
        self._title = inter_wiki.get("title", '').removeprefix(f'{inter_wiki.get("iw", "")}:')
        self._page_url = inter_wiki.get("url", '')
        self._interwiki = True

    async def _handle_disambiguation(self) -> list:
        # 截取正文中位于**行首**的内链，以排除非消歧义链接
        # （因为一般的消歧义页面，条目名都在行首）
        # 思路来自于 https://github.com/wikimedia/pywikibot/blob/master/scripts/solve_disambiguation.py
        wikitext = await self._wikitext()
        found_list = []

        reg = compile(r'\*.*?\[\[(.*?)(?:\||]])')
        for line in wikitext.splitlines():
            found = reg.match(line)
            if found:
                found_list.append(found.group(1))

        return found_list

    async def _handle_missing_page(self) -> list:
        self._missing = True
        search = await self.search(self._title, suggestion=False)
        if search:
            return search
        else:
            raise PageError(title=self._title)

    @staticmethod
    def handle_anchor_pre_process(title: str) -> tuple:
        anchor_list = re.split('#', title, maxsplit=1)
        new_title = anchor_list[0]
        anchor = anchor_list[1] if len(anchor_list) > 1 else ''

        return new_title, anchor

    @staticmethod
    def handle_anchor_post_process(url: str, anchor: str) -> str:
        new_url = f"{url}#{parse.quote(anchor)}" if anchor else url
        return new_url
