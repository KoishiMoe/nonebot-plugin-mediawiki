# screenshot_tester.py
import asyncio
import urllib.parse
from typing import Optional

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Error


class ScreenshotTester:
    """Standalone screenshot tester extracted from worker.py"""

    def __init__(
            self,
            browser_type: str = "chromium",
            headless: bool = True,
            proxy: Optional[str] = None,
            language: str = "zh-CN",
            viewport_width: int = 1920,
            viewport_height: int = 1080,
            timeout: float = 30.0,
            wait_until: str = "load",
            split_pages: int = 0,
            jpeg_quality: int = 80,
    ):
        self.browser_type = browser_type.lower()
        self.headless = headless
        self.proxy = proxy
        self.language = language
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.timeout = timeout
        self.wait_until = wait_until
        self.split_pages = split_pages
        self.jpeg_quality = jpeg_quality

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.browser_context: Optional[BrowserContext] = None

    async def initialize(self):
        """Initialize playwright and browser"""
        self.playwright = await async_playwright().start()

        launch_arguments = {"headless": self.headless}

        if self.proxy:
            p = urllib.parse.urlparse(self.proxy)
            proxy_config = {
                "server": f"{p.scheme}://{p.hostname}:{p.port}",
                "username": p.username,
                "password": p.password
            }
            launch_arguments["proxy"] = proxy_config

        if self.browser_type == "firefox":
            self.browser = await self.playwright.firefox.launch(**launch_arguments)
        elif self.browser_type == "webkit":
            self.browser = await self.playwright.webkit.launch(**launch_arguments)
        else:
            self.browser = await self.playwright.chromium.launch(**launch_arguments)

        self.browser_context = await self.browser.new_context(
            locale=self.language,
            viewport={"width": self.viewport_width, "height": self.viewport_height},
        )

    async def cleanup(self):
        """Clean up resources"""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def screenshot_url(self, url: str) -> list[bytes]:
        """Take screenshot(s) of a URL

        Returns:
            List of screenshot bytes (JPEG format)
        """
        if not self.browser or not self.browser_context:
            raise RuntimeError("Browser not initialized. Call initialize() first.")

        screenshots = []
        pg: Optional[Page] = None

        try:
            pg = await self.browser_context.new_page()

            await pg.goto(url, timeout=self.timeout * 1000, wait_until=self.wait_until)

            if self.split_pages > 0:
                # Use a small initial height to load content first
                initial_height = 800
                await pg.set_viewport_size({"width": self.viewport_width, "height": initial_height})

                # Calculate actual content height
                # https://stackoverflow.com/a/1147768
                content_height = await pg.evaluate(
                    "Math.max(document.body.scrollHeight, document.body.offsetHeight, "
                    "document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight );")
                print(content_height)

                # Get configured max height (use the browser height config as max)
                max_height = self.viewport_height

                if content_height > max_height:
                    # Content exceeds max height, use split logic
                    await pg.set_viewport_size({"width": self.viewport_width, "height": max_height})

                    page_num = 1
                    fail_count = 0
                    viewport_height = await pg.evaluate("window.innerHeight")
                    last_scroll_y = -1

                    while True:
                        current_scroll_y = await pg.evaluate("window.scrollY")
                        if current_scroll_y == last_scroll_y:
                            break
                        last_scroll_y = current_scroll_y

                        try:
                            img = await pg.screenshot(full_page=False, type="jpeg", quality=self.jpeg_quality)
                            screenshots.append(img)
                            page_num += 1
                            fail_count = 0

                            if page_num > self.split_pages:
                                break
                        except Exception as e:
                            fail_count += 1
                            if fail_count >= 3:
                                raise e
                            continue

                        await pg.evaluate(f"window.scrollBy(0, {viewport_height});")
                        await pg.wait_for_timeout(250)
                else:
                    # Content fits within max height, take single screenshot
                    await pg.set_viewport_size({"width": self.viewport_width, "height": content_height})
                    img = await pg.screenshot(full_page=True, type="jpeg", quality=80)
                    screenshots.append(img)
            else:
                img = await pg.screenshot(full_page=True, type="jpeg", quality=self.jpeg_quality)
                screenshots.append(img)

        finally:
            if pg:
                await pg.close()

        return screenshots


async def main():
    """Example usage"""
    tester = ScreenshotTester(
        browser_type="chromium",
        split_pages=20,
        timeout=30.0,
        viewport_width=1920,
        viewport_height=1080,
    )

    try:
        await tester.initialize()
        screenshots = await tester.screenshot_url("https://zh.wikipedia.org")

        for i, screenshot in enumerate(screenshots):
            with open(f"screenshot_{i}.jpg", "wb") as f:
                f.write(screenshot)

        print(f"Captured {len(screenshots)} screenshot(s)")

    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
