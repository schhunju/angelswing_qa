"""Shared page helpers for EMI calculator page objects."""

from __future__ import annotations

from playwright.sync_api import Locator, Page, expect

from config.settings import BASE_URL, RECALC_WAIT_MS
from pages.driver_setup import DriverSetup


class BasePage:
    def __init__(self, driver: DriverSetup) -> None:
        self.driver = driver

    @property
    def page(self) -> Page:
        return self.driver.page

    def navigate(self, url: str = BASE_URL) -> None:
        self.page.goto(url)

    def click(self, selector: str) -> None:
        self.driver.locator(selector).click()

    def get_text(self, selector: str) -> str:
        return self.driver.locator(selector).inner_text()

    def wait_for_visible(self, selector: str) -> None:
        expect(self.driver.locator(selector)).to_be_visible()

    def wait_for_recalc(self, ms: int = RECALC_WAIT_MS) -> None:
        self.driver.wait(ms)

    def set_slider_by_value(
        self, slider: Locator, target: float, min_val: float, max_val: float
    ) -> None:
        """Drag jQuery UI slider handle to proportional position for target value."""
        # Bring slider into view so bounding boxes reflect on-screen coordinates.
        slider.scroll_into_view_if_needed()
        track_box = slider.bounding_box()
        if not track_box:
            raise RuntimeError("Slider bounding box not available")

        # jQuery UI sliders expose a draggable handle, not the track itself.
        handle = slider.locator(".ui-slider-handle")
        handle_box = handle.bounding_box()
        if not handle_box:
            raise RuntimeError("Slider handle not found")

        # Map target value (e.g. ₹10L) to a 0–1 position along the slider track.
        ratio = (target - min_val) / (max_val - min_val)
        ratio = max(0.0, min(1.0, ratio))  # clamp for safety at min/max bounds

        # Compute drag start (handle center) and end (target point on track).
        end_x = track_box["x"] + track_box["width"] * ratio
        y = track_box["y"] + track_box["height"] / 2
        start_x = handle_box["x"] + handle_box["width"] / 2
        start_y = handle_box["y"] + handle_box["height"] / 2

        # Drag handle to target position; site recalculates EMI on slider change.
        self.page.mouse.move(start_x, start_y)
        self.page.mouse.down()
        self.page.mouse.move(end_x, y)
        self.page.mouse.up()
        self.wait_for_recalc()
