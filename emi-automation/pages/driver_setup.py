"""Playwright driver wrapper used by all page objects."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from config.settings import DEFAULT_TIMEOUT_MS, RECALC_WAIT_MS


class DriverSetup:
    def __init__(self, page: Page) -> None:
        self.page = page
        self.page.set_default_timeout(DEFAULT_TIMEOUT_MS)

    def locator(self, selector: str) -> Locator:
        return self.page.locator(selector)

    def wait(self, ms: int = RECALC_WAIT_MS) -> None:
        self.page.wait_for_timeout(ms)
