"""Open the one app URL; reset balance; thin API helper for data."""

from __future__ import annotations

import os

# Prefer the normal Playwright browser cache (e.g. after `playwright install chromium`).
# Some environments set PLAYWRIGHT_BROWSERS_PATH to an empty isolated dir → missing binaries.
os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
from pathlib import Path

import pytest
from dotenv import load_dotenv

from automation.api_client import BettingAPI

load_dotenv(Path(__file__).resolve().parent / ".env")


def _env_headed() -> bool:
    """True when .env sets PLAYWRIGHT_HEADED=1|true|yes|on (case-insensitive)."""
    v = os.environ.get("PLAYWRIGHT_HEADED", "").strip().lower()
    return v in ("1", "true", "yes", "on")


@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig: pytest.Config) -> dict:
    """Mirror pytest-playwright launch options + PLAYWRIGHT_HEADED from .env."""
    launch_options: dict = {}
    if pytestconfig.getoption("--headed", default=False) or _env_headed():
        launch_options["headless"] = False
    ch = pytestconfig.getoption("--browser-channel", default=None)
    if ch:
        launch_options["channel"] = ch
    slow = pytestconfig.getoption("--slowmo", default=None)
    if slow:
        launch_options["slow_mo"] = int(slow)
    return launch_options


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "https://qae-assignment-tau.vercel.app").rstrip("/")


@pytest.fixture(scope="session")
def user_id() -> str:
    return os.environ.get("USER_ID", "candidate-Z1tPv7cRx5K")


@pytest.fixture(scope="session")
def api(base_url: str, user_id: str) -> BettingAPI:
    return BettingAPI(base_url, user_id)


@pytest.fixture(autouse=True)
def _reset_balance(request: pytest.FixtureRequest, api: BettingAPI) -> None:
    if request.node.get_closest_marker("no_reset"):
        return
    api.reset_balance()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict, base_url: str) -> dict:
    return {
        **browser_context_args,
        "base_url": base_url,
        "viewport": {"width": 1440, "height": 900},
        "locale": "en-GB",
    }


@pytest.fixture
def app(page, base_url: str, user_id: str):
    """Single page: SPA with ?user-id= (same URL for every test)."""
    page.goto(f"/?user-id={user_id}", wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_selector("#match-list", timeout=60_000)
    try:
        page.locator("#match-list-loading").wait_for(state="hidden", timeout=15_000)
    except Exception:
        pass
    page.wait_for_selector("[id^='match-card-']", timeout=60_000)
    yield page
