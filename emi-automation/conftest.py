"""Pytest fixtures for EMI calculator automation."""

from __future__ import annotations

import base64
import logging
import shutil
from pathlib import Path

import pytest
from pytest_html import extras as html_extras

from config.settings import BASE_URL
from pages.driver_setup import DriverSetup
from pages.emi_calculator_page import EmiCalculatorPage

logger = logging.getLogger(__name__)
REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def pytest_sessionstart(session) -> None:
    """Clear previous HTML report and screenshots before each run."""
    # Remove stale report.html and PNGs from the last run.
    if REPORTS_DIR.exists():
        shutil.rmtree(REPORTS_DIR)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Cleared reports directory: %s", REPORTS_DIR)


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict) -> dict:
    # Open browser maximized in headed mode.
    launch_args = list(browser_type_launch_args.get("args", []))
    if "--start-maximized" not in launch_args:
        launch_args.append("--start-maximized")
    return {**browser_type_launch_args, "args": launch_args}


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    # no_viewport lets the page fill the maximized window.
    return {
        **browser_context_args,
        "no_viewport": True,
        "base_url": BASE_URL,
        "accept_downloads": True,
    }


@pytest.fixture
def driver_setup(page) -> DriverSetup:
    """Shared Playwright driver wrapper for all page objects."""
    return DriverSetup(page)


@pytest.fixture
def app_page(driver_setup: DriverSetup) -> EmiCalculatorPage:
    """Default application page — opens calculator and selects Home Loan tab."""
    page = EmiCalculatorPage(driver_setup)
    page.open()
    page.ensure_home_loan_tab()
    return page


def _get_playwright_page(item) -> object | None:
    """Return the Playwright page used by a test, for post-test screenshots."""
    # item.funcargs holds fixture values injected into the test (e.g. app_page).
    driver = item.funcargs.get("driver_setup")
    app = item.funcargs.get("app_page")
    page = item.funcargs.get("page")

    # Prefer driver_setup — all page objects share this wrapper.
    if driver is not None:
        return driver.page
    # Fallback: page object fixture without direct driver_setup reference.
    if isinstance(app, EmiCalculatorPage):
        return app.driver.page
    # Last resort: raw pytest-playwright page fixture.
    if page is not None:
        return page
    return None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """After each test: save screenshot and attach it to the HTML report."""
    # Let pytest finish the test and build the report object first.
    outcome = yield
    report = outcome.get_result()

    # Screenshot only after the test body runs — not setup/teardown; skip skipped tests.
    if report.when != "call" or report.skipped:
        return

    playwright_page = _get_playwright_page(item)
    if playwright_page is None:
        return

    # Capture final browser state for both pass and fail.
    status = "passed" if report.passed else "failed"
    REPORTS_DIR.mkdir(exist_ok=True)
    screenshot_path = REPORTS_DIR / f"{item.name}_{status}.png"
    screenshot_bytes = playwright_page.screenshot(path=str(screenshot_path))

    # Embed screenshot in report.html (--self-contained-html uses base64).
    report.extras = getattr(report, "extras", [])
    report.extras.append(
        html_extras.png(
            base64.b64encode(screenshot_bytes).decode(),
            name=f"Screenshot ({status})",
        )
    )
    logger.info("Screenshot saved (%s): %s", status, screenshot_path)
