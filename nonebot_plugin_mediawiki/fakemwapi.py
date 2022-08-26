from urllib import parse


class DummyPage:
    def __init__(self, url: str, title: str):
        self._title = title
        self._url = f"{url}/{parse.quote(title)}"

    @property
    def title(self):
        return self._title

    @property
    def url(self):
        return self._url


class DummyMediaWiki:
    def __init__(self, url: str):
        self._url = url

    async def page(self, title: str, *args, **kwargs) -> DummyPage:
        return DummyPage(self.url, title)

    @property
    def url(self):
        return self._url
