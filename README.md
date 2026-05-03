# qa-betting-sg

Take-home: single-bet football web app — test plan, bugs, short strategy, and two Pytest Playwright(Chromium) tests against the hosted URL.

## Contents

| Item | Path |
|------|------|
| Test plan | [docs/test-plan.md](docs/test-plan.md) |
| Bug reports | [docs/bug-reports.md](docs/bug-reports.md) |
| Strategy | [docs/strategy.md](docs/strategy.md) |
| Automation | [automation/](automation/) |

## Run the tests

Python 3.10+. From repo root:

```bash
cd automation
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -e .
./.venv/bin/playwright install chromium
cp .env.example .env   # optional: BASE_URL, USER_ID, PLAYWRIGHT_HEADED
```

```bash
cd automation
PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_betting.py -v
```

After a run, open `automation/reports/report.html` for the pytest-html summary (self-contained; directory is gitignored).

Headed browser: add `--headed` or set `PLAYWRIGHT_HEADED=true` in `automation/.env`. Details: [automation/README.md](automation/README.md).

## App

- `https://qae-assignment-tau.vercel.app/?user-id=<your-id>`
- API docs: `/api/docs` on the same host

Use the candidate id from the assignment in the URL and in `USER_ID` for tests.
