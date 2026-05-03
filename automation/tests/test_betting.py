"""
Two Playwright tests against the hosted betting SPA (see conftest.py).

Fixtures (from conftest.py):
  app   — Browser page already opened on /?user-id=… with the match list ready.
  api   — HTTP helper (same BASE_URL / USER_ID); balance is reset before each test.

Tests:
  1) Happy path — HOME selection, €10 stake, success modal + balance debited via API.
  2) Stake rule — €0.99 shows the minimum-stake warning on the slip (no bet placed).
"""

from __future__ import annotations

from playwright.sync_api import expect


def _odds(match_id: str, selection: str) -> str:
    """CSS selector for a match outcome button (HOME / DRAW / AWAY → lower-case in DOM)."""
    return f"#odds-{match_id}-{selection.lower()}"


def test_place_bet_happy_path(app, api) -> None:
    """End-to-end: place a valid bet and confirm receipt fields + wallet movement."""
    # Arrange: first match from API (ids and odds are not hard-coded in the repo).
    m0 = api.matches()[0]
    match_id = m0["id"]
    home_odds = float(m0["odds"]["home"])
    before = float(api.balance()["balance"])

    # Act: pick home, enter max two-decimal stake, submit.
    app.locator(_odds(match_id, "HOME")).click()
    app.locator("#bet-slip-stake-input").fill("10.00")
    app.locator("#bet-slip-place-bet").click()

    # Assert: success modal visible (network + UI can be slow on cold start).
    expect(app.locator("#modal-success")).to_be_visible(timeout=60_000)
    assert app.locator("#modal-success-bet-id").inner_text().strip()
    assert m0["homeTeam"] in app.locator("#modal-success-match").inner_text()
    assert app.locator("#modal-success-stake").inner_text() == "€10.00"
    assert app.locator("#modal-success-odds").inner_text().strip() == f"{home_odds:.2f}"
    payout_txt = app.locator("#modal-success-payout").inner_text().strip()
    assert payout_txt.startswith("€")
    assert app.locator("#modal-success-placed-at").inner_text().strip()

    # Wallet should drop by stake (small float tolerance for API rounding).
    after = float(api.balance()["balance"])
    assert abs(after - (before - 10.0)) < 0.02

    app.locator("#modal-success-close").click()
    expect(app.locator("#modal-success")).to_be_hidden()


def test_stake_below_minimum_shows_warning(app, api) -> None:
    """UI blocks below-minimum stake: slip shows warning, no placement required."""
    match_id = api.matches()[0]["id"]
    app.locator(_odds(match_id, "HOME")).click()
    app.locator("#bet-slip-stake-input").fill("0.99")
    expect(app.locator(".stakeWarning")).to_contain_text("Minimum stake")
