from .mediawiki.exceptions import MediaWikiBaseException


class NoDefaultPrefixException(MediaWikiBaseException):
    def __init__(self, group: int = None):
        self._group = group
        msg = f"群{group}没有配置默认的Wiki前缀"
        super(NoDefaultPrefixException, self).__init__(msg)

    @property
    def group(self):
        return self._group


class NoSuchPrefixException(MediaWikiBaseException):
    def __init__(self, group: int = None, prefix: str = None):
        self._group = group
        self._prefix = prefix
        msg = f"群{group}的wiki列表以及全局列表中均不存在前缀{prefix}"
        super(NoSuchPrefixException, self).__init__(msg)

    @property
    def group(self):
        return self._group

    @property
    def prefix(self):
        return self._prefix
