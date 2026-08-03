from playwright.sync_api import sync_playwright


class PlaywrightClient:

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self, headless: bool = False):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=headless
        )

        self.page = self.browser.new_page()

    def open(self, url: str):

        self.page.goto(url)

    def click(self, text: str):

        self.page.get_by_text(
            text,
            exact=False,
        ).click()

    def fill(self, label: str, value: str):

        self.page.get_by_label(
            label,
            exact=False,
        ).fill(value)

    def verify_visible(self, text: str):

        assert self.page.get_by_text(
            text,
            exact=False,
        ).is_visible()

    def verify_title(self, title: str):

        assert title in self.page.title()

    def screenshot(self, path: str):

        self.page.screenshot(path=path)

    def stop(self):

        self.browser.close()

        self.playwright.stop()