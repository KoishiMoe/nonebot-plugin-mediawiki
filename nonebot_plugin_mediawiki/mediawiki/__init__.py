"""
mediawiki module initialization
"""
import asyncio
import platform

from .constants import URL, VERSION
from .exceptions import (
    MediaWikiException,
    PageError,
    MediaWikiGeoCoordError,
    RedirectError,
    DisambiguationError,
    MediaWikiAPIURLError,
    HTTPTimeoutError,
    MediaWikiCategoryTreeError,
    MediaWikiLoginError,
)
from .mediawiki import MediaWiki
from .mediawikipage import MediaWikiPage

__author__ = "KoishiMoe"
__maintainer__ = "KoishiMoe"
__license__ = "MIT"
__version__ = VERSION
__credits__ = ["Tyler Barrus", "Jonathan Goldsmith"]
__url__ = URL
__bugtrack_url__ = "{0}/issues".format(__url__)
__download_url__ = "{0}/tarball/v{1}".format(__url__, __version__)

__all__ = [
    "MediaWiki",
    "MediaWikiPage",
    "PageError",
    "RedirectError",
    "MediaWikiException",
    "DisambiguationError",
    "MediaWikiAPIURLError",
    "HTTPTimeoutError",
    "MediaWikiGeoCoordError",
    "MediaWikiCategoryTreeError",
    "MediaWikiLoginError",
]

# fix some proxy issues on Windows
if "windows" in platform.system().lower():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
