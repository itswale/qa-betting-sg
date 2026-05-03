# Automation

Two tests: Playwright + pytest, one base URL with `?user-id=…`.

## Setup

From `automation/` (where `pyproject.toml` lives):

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -e .
./.venv/bin/playwright install chromium
cp .env.example .env   # optional
```

Use `./.venv/bin/python -m pytest` so the project venv is the one running (avoids a different global Python without pytest).

Headed: `PLAYWRIGHT_HEADED=true` in `.env`, or pass `--headed`. `--headed` wins for that run.

## Run

From `automation/` (so `reports/` lands next to `pyproject.toml`):

```bash
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_betting.py -v
```

Each run writes a **self-contained HTML report** to `reports/report.html` (overwrites the previous run). Open it in a browser. The folder is gitignored.

To skip the report for one run: `pytest … -p no:html` (disables pytest-html).

Inspector: `PWDEBUG=1` … same command, with `--headed` if you like.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| No module named pytest | Run pytest via `./.venv/bin/python -m pytest` after `pip install -e .` |
| No `.venv` | `python3 -m venv .venv` in `automation/` |
| Browser executable missing | `./.venv/bin/playwright install chromium` |

## Env

| Variable | Default |
|----------|---------|
| `BASE_URL` | `https://qae-assignment-tau.vercel.app` |
| `USER_ID` | `candidate-Z1tPv7cRx5K` |

## Tests

| Test | Does |
|------|------|
| `test_place_bet_happy_path` | HOME, stake 10.00, success modal, balance |
| `test_stake_below_minimum_shows_warning` | 0.99 → minimum stake warning |
