# from dotenv import load_dotenv

from nonebot import logger, get_driver

from . import config_manager
from . import worker

# 接入帮助系统
__usage__ = '使用：\n' \
            '快速使用：wiki 前缀:条目名\n' \
            '查询条目/模板：[[前缀:条目名]] {{前缀:模板名}} ((前缀:条目名))\n' \
            '截图：wiki.shot 前缀:条目名\n' \
            '其中中括号、大括号匹配后会调用api搜索条目/模板名，如果有误，可以使用小括号方式绕过api直接生成链接\n' \
            '前缀由群管和bot超管配置，没有指定前缀或前缀无效时，会回落到默认前缀\n' \
            '配置：\n' \
            '添加：wiki.add <前缀> <api地址（可选）> <通用url地址> < -g（若添加该参数，则操作全局wiki，需要超管权限，下同）>\n' \
            '删除：wiki.delete <前缀> < -g >\n' \
            '列表：wiki.list < -g >\n' \
            '设置默认：wiki.default <前缀> < -g >\n' \
            '按提示提供相应参数即可\n' \
            '注意：私聊状态下该插件仅会响应超管的命令，且仅能管理全局wiki\n' \
            '完整文档请前往 https://github.com/KoishiMoe/nonebot-plugin-mediawiki 查看'

__help_version__ = '1.2.2'

__help_plugin_name__ = 'Wiki推送'

# load_dotenv()  # Dont do this, nonebot has its own logic.

# if os.getenv("WIKI_PROXY"):
#     logger.info(f"Wiki: using proxy {os.getenv('WIKI_PROXY')}")

try:
    logger.info(f"Wiki: using proxy {get_driver().config.wiki_proxy}")
except AttributeError:
    get_driver().config.wiki_proxy = None


try:
    from nonebot.plugin import PluginMetadata

    __plugin_meta__ = PluginMetadata(
        name=__help_plugin_name__,
        description="适用于 nonebot2 的 MediaWiki 查询插件",
        usage=__usage__,
        homepage="https://github.com/KoishiMoe/nonebot-plugin-mediawiki",
        type="application",
        extra={},
        supported_adapters={"~onebot.v11"},
    )
except ImportError:
    pass
