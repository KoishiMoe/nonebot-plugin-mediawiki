import json
import os
from pathlib import Path

from .exception import NoSuchPrefixException, NoDefaultPrefixException

WIKI_DIR = Path("") / "data" / "database" / "wiki"


class Config:
    def __init__(self, group_id: int):
        self.__gid = group_id
        self.__default: str = ""
        self.__default_global: str = ""
        self.__wikis: dict = {}
        self.__wikis_global: dict = {}

        self.__parse_data(self.__get_config())
        self.__parse_global_data(self.__get_global_config())

    def add_wiki(self, prefix: str, api_url: str, url: str) -> bool:
        self.__wikis[prefix] = [api_url, url]
        if self.__default == "":
            self.__default = prefix

        return self.save_data()

    def add_wiki_global(self, prefix: str, api_url: str, url: str) -> bool:
        self.__wikis_global[prefix] = [api_url, url]
        if self.__default_global == "":
            self.__default_global = prefix

        return self.save_global_data()

    def del_wiki(self, prefix: str) -> bool:
        if prefix == self.__default:
            self.__default = ""
        return self.__wikis.pop(prefix, "") != "" and self.save_data()

    def del_wiki_global(self, prefix: str) -> bool:
        if prefix == self.__default_global:
            self.__default_global = ""
        return self.__wikis_global.pop(prefix, "") != "" and self.save_global_data()

    def __get_config(self) -> dict:
        file_name = f'{self.__gid}.json'
        return self.__get_config_parse(file_name)

    def __get_global_config(self) -> dict:
        file_name = 'global.json'
        return self.__get_config_parse(file_name)

    @staticmethod
    def __get_config_parse(file_name: str) -> dict:
        path = WIKI_DIR / file_name
        if not WIKI_DIR.is_dir():
            os.makedirs(WIKI_DIR)
        if not path.is_file():
            with open(path, "w", encoding="utf-8") as w:
                w.write(json.dumps({}))
        data = json.loads(path.read_bytes())
        return data

    def __parse_data(self, data: dict):
        self.__default = data.get("default", "")
        self.__wikis = data.get("wikis", {})

    def __parse_global_data(self, data: dict):
        self.__default_global = data.get("default", "")
        self.__wikis_global = data.get("wikis", {})

    def get_from_prefix(self, prefix: str) -> list:
        if prefix == "":  # 没有匹配到前缀，尝试使用默认前缀
            if self.__default == "" and self.__default_global == "":  # 没有配置默认前缀
                raise NoDefaultPrefixException
            if self.__default != "":  # 本群设置了默认前缀
                temp_data: list = self.__wikis.get(self.__default, None)
                if not temp_data:  # 没有从本群的列表中找到对应wiki,回落到全局
                    temp_global_data = self.__wikis_global.get(self.__default, None)
                    if not temp_global_data:
                        raise NoSuchPrefixException
                    return temp_global_data
                return temp_data
            # 有全局默认前缀（此时强制使用全局数据库）
            temp_global_data: list = self.__wikis_global.get(self.__default_global, None)
            if not temp_global_data:
                raise NoSuchPrefixException
            return temp_global_data

        temp_data: list = self.__wikis.get(prefix, None)
        if not temp_data:
            temp_global_data = self.__wikis_global.get(prefix, None)
            if not temp_global_data:
                raise NoSuchPrefixException
            return temp_global_data
        return temp_data

    def save_data(self) -> bool:
        file_name = f"{self.__gid}.json"
        data: dict = {"default": self.__default, "wikis": self.__wikis}
        return self.__save_data_parse(file_name, data)

    def save_global_data(self) -> bool:
        file_name = "global.json"
        data: dict = {"default": self.__default_global, "wikis": self.__wikis_global}
        return self.__save_data_parse(file_name, data)

    @staticmethod
    def __save_data_parse(file_name: str, data: dict) -> bool:
        path = WIKI_DIR / file_name
        if not path.is_file():
            with open(path, "w", encoding="utf-8") as w:
                w.write(json.dumps({}))
        with open(path, "w", encoding="utf-8") as w:
            w.write(json.dumps(data, indent=4))
        return True

    def set_default(self, default: str) -> bool:
        if default in self.__wikis:
            self.__default = default
            self.save_data()
            return True
        return False

    def set_default_global(self, default: str) -> bool:
        if default in self.__wikis_global:
            self.__default_global = default
            self.save_global_data()
            return True
        return False

    @property
    def list_data(self) -> tuple:
        count: int = 0
        temp_list: str = ""
        temp_list += f"本群默认：{self.__default}\n"
        temp_list += "本群所有wiki：\n"
        for prefix in self.__wikis:
            count += 1
            temp_str: str = f"{count}.前缀：{prefix}\n" + \
                            f"API地址：{self.__wikis.get(prefix)[0]}\n" + \
                            f"通用链接：{self.__wikis.get(prefix)[1]}\n"
            temp_list += temp_str

        count = 0
        temp_list_global: str = ""
        temp_list_global += f"全局默认：{self.__default_global}\n"
        temp_list_global += "所有全局wiki：\n"
        for prefix in self.__wikis_global:
            count += 1
            temp_str: str = f"{count}.前缀：{prefix}\n" + \
                            f"API地址：{self.__wikis_global.get(prefix)[0]}\n" + \
                            f"通用链接：{self.__wikis_global.get(prefix)[1]}\n"
            temp_list_global += temp_str

        return temp_list, temp_list_global

    @property
    def prefixes(self) -> set:
        prefixes = set(self.__wikis.keys()).union(set(self.__wikis_global.keys()))
        return prefixes
