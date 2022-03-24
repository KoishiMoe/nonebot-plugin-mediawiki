from .utilities import str_or_unicode


class MediaWikiBaseException(Exception):
    """ Base MediaWikiException

        Args:
            message: The message of the exception """

    def __init__(self, message):
        self._message = message
        super(MediaWikiBaseException, self).__init__(self.message)

    def __unicode__(self):
        return self.message

    def __str__(self):
        return str_or_unicode(self.__unicode__())

    @property
    def message(self):
        """ str: The MediaWiki exception message """
        return self._message


class MediaWikiException(MediaWikiBaseException):
    """ MediaWiki Exception Class

        Args:
            error (str): The error message that the MediaWiki site returned """

    def __init__(self, error):
        self._error = error
        msg = 'An unknown error occurred: "{0}". Please report it on GitHub!'.format(
            self.error
        )
        super(MediaWikiException, self).__init__(msg)

    @property
    def error(self):
        """ str: The error message that the MediaWiki site returned """
        return self._error


class HTTPTimeoutError(MediaWikiBaseException):
    """ Exception raised when a request to the Mediawiki site times out.

        Args:
            query (str): The query that timed out"""

    def __init__(self, query):
        self._query = query
        msg = (
            'Searching for "{0}" resulted in a timeout. '
            "Try again in a few seconds, and ensure you have rate limiting "
            "set to True."
        ).format(self.query)
        super(HTTPTimeoutError, self).__init__(msg)

    @property
    def query(self):
        """ str: The query that timed out """
        return self._query


class MediaWikiGeoCoordError(MediaWikiBaseException):
    """ Exceptions to handle GeoData exceptions

        Args:
            error (str): Error message from the MediaWiki site related to \
                         GeoCoordinates """

    def __init__(self, error):
        self._error = error
        msg = (
            "GeoData search resulted in the following error: {0}"
            " - Please use valid coordinates or a proper page title."
        ).format(self.error)
        super(MediaWikiGeoCoordError, self).__init__(msg)

    @property
    def error(self):
        """ str: The error that was thrown when pulling GeoCoordinates """
        return self._error


class PageError(MediaWikiBaseException):
    """ Exception raised when no MediaWiki page matched a query

        Args:
            title (str): Title of the page
            pageid (int): MediaWiki page id of the page"""

    def __init__(self, title=None, pageid=None):
        if title:
            self._title = title
            msg = '"{0}" does not match any pages. Try another query!'.format(
                self._title
            )
        elif pageid:
            self._pageid = pageid
            msg = 'Page id "{0}" does not match any pages. Try another id!'.format(
                self._pageid
            )
        else:
            self._title = ""
            msg = '"{0}" does not match any pages. Try another query!'.format(
                self._title
            )
        super(PageError, self).__init__(msg)


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
