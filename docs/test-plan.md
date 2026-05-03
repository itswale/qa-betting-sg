# Test plan — single bet placement

Desktop web, football, pre-match, single bet. Money in EUR; API uses `x-user-id` on the same host as the UI.

Each scenario: **ID**, **priority** (**Highest** → run first / blocking path; **High** → important next; **Lower** → second pass), **preconditions**, **steps**, **expected**, **assignment** (FR /   from the brief).

### Postman / API

For any `GET` / `POST` below, use Postman (or another HTTP client) with the same base URL as the app and header `x-user-id` equal to `?user-id=` in the browser. Raw JSON body where needed. Full examples with evidence: [bug-reports.md](bug-reports.md#reproducing-api-behaviour-with-postman).

| Setting | Value |
|---------|--------|
| Base URL | `https://qae-assignment-tau.vercel.app` (or your deploy) |
| Header | `x-user-id` = browser `?user-id=` |
| JSON | Body → raw → JSON |

| Method | Path | Body |
|--------|------|------|
| GET | `/api/matches` | — |
| GET | `/api/balance` | — |
| POST | `/api/reset-balance` | none |
| POST | `/api/place-bet` | `matchId`, `selection` (HOME / DRAW / AWAY), `stake` |

---

## TC-01 — Place a single bet (happy path)

| Field | Value |
|--------|--------|
| **ID** | TC-01 |
| **Priority** | Highest |
| **Preconditions** | Enough balance (`GET …/api/balance`). At least one match (`GET …/api/matches`). Optional: `POST …/api/reset-balance` for a known balance. |
| **Steps** | 1. Open app with valid `?user-id=`. 2. Pick 1, X, or 2 on one match. 3. Stake between €1.00 and €100.00 (e.g. €10.00). 4. Place bet. 5. If shown, Placing… then success receipt. 6. Close receipt. |
| **Expected** | Balance decreases. Receipt shows bet id, match, stake, odds, potential payout, time. After close, slip empty or no active bet. |
| **Assignment** | FR 2.1–2.4; stake  4.1 |

**Automated:** `automation/tests/test_betting.py` → `test_place_bet_happy_path` (HOME, €10; receipt fields the test asserts, balance via API). Not a full manual receipt audit.<img width="733" height="252" alt="Screenshot 2026-05-03 at 3 17 57 PM" src="https://github.com/user-attachments/assets/b97785d7-cb31-4d1b-93b0-2c389bdbf88e" />


---

## TC-02 — Stake validation

| Field | Value |
|--------|--------|
| **ID** | TC-02 |
| **Priority** | Highest |
| **Preconditions** | Selection on slip. Use `GET …/api/matches` if you need `matchId` for API rows. |
| **Steps** | Per row: enter stake in UI or `POST …/api/place-bet` in Postman; note message and status. |
| **Expected** | Bad stakes blocked or clearly messaged; bad bodies return 422 (or spec status) with clear errors. |

| Case | Stake | UI | API |
|------|-------|-----|-----|
| Below minimum | €0.99 | Min stake message | 422 `invalid_stake_min` (seen on host) |
| Minimum | €1.00 | OK | 200 |
| Maximum | €100.00 | OK | 200 |
| Above maximum | €100.01 | Max message | 422 `invalid_stake_max` (seen) |
| Too many decimals | €10.123 | Error / warning | 422 `invalid_stake_precision` (seen) |
| Non-numeric | abc | Not accepted | Error if sent badly |
| Empty | Clear field | Disabled / blocked | 422 if bad request |
| Over balance | stake above wallet | Insufficient message | Should reject — [bug-reports.md](bug-reports.md) if not |

**Assignment:** 4.1,  4.4  

**Automated:** `test_stake_below_minimum_shows_warning` only (€0.99 → minimum copy). Rest manual or Postman.<img width="733" height="252" alt="Screenshot 2026-05-03 at 3 17 57 PM" src="https://github.com/user-attachments/assets/b97785d7-cb31-4d1b-93b0-2c389bdbf88e" />

---

## TC-03 — Place bet fails; error modal

| Field | Value |
|--------|--------|
| **ID** | TC-03 |
| **Priority** | Highest |
| **Preconditions** | Valid slip. Force failure via devtools, proxy, or Playwright (e.g. 500 on `place-bet`) if possible. |
| **Steps** | Submit; read title/body; Rebet; fail again; Close and ×. |
| **Expected** | Title “Something went wrong”; body useful; Rebet retries; Close / × clear per FR 2.5. |
| **Assignment** | FR 2.5 |

**Automated:** No.

---

## TC-04 — Bet slip

| Field | Value |
|--------|--------|
| **ID** | TC-04 |
| **Priority** | High |
| **Preconditions** | List loaded. |
| **Steps** | 1 on A → one line; X on same match replaces; 2 on B → still one selection; row ×; add again; Remove All; change stake and watch totals / payout. |
| **Expected** | Single selection; replace works; remove works; numbers update. |
| **Assignment** | FR 2.1, 2.2 |

**Automated:** Only where happy path touches the slip.

---

## TC-05 — Filters

| Field | Value |
|--------|--------|
| **ID** | TC-05 |
| **Priority** | High |
| **Preconditions** | Default list; note “Showing … matches”. |
| **Steps** | Single day; date range (inclusive); odds min/max; min > max should error; each time compare count to visible rows. |
| **Expected** | FR 2.6; count matches list ([bug-reports.md](bug-reports.md) if not). |
| **Assignment** | FR 2.6 |

**Automated:** No.

---

## TC-06 — API negatives

| Field | Value |
|--------|--------|
| **ID** | TC-06 |
| **Priority** | Lower |
| **Preconditions** | Postman; `x-user-id` matches UI when comparing to browser. |
| **Steps** | Run each check; compare status/body to OpenAPI /  5. |
| **Expected** | Matches spec. |

| Check | Postman | Expected |
|-------|---------|----------|
| Matches | GET `…/api/matches` + `x-user-id` | 200, array |
| Balance | GET `…/api/balance` + header | 200, balance + currency |
| No user header | POST `…/api/place-bet`, omit `x-user-id` | 401 |
| Bad matchId | POST + bogus `matchId` | 422 |
| Bad JSON | POST + invalid raw body | 400 |
| Wrong method | GET on `…/api/place-bet` | 405 |
| Double submit | Two overlapping POSTs if applicable | 409 if reproducible |
| Reset | POST `…/api/reset-balance` then GET balance | 200; balance matches reset |

**Assignment:**  5  

**Automated:** No.

---

## Execution summary

| Scenario | Coverage |
|----------|----------|
| TC-01 happy path | `test_place_bet_happy_path` |
| TC-02 min stake UI | `test_stake_below_minimum_shows_warning` |
| TC-02 other rows, TC-03–TC-06 | Manual / Postman; bugs in [bug-reports.md](bug-reports.md) |

Run the two tests: root [README.md](../README.md) or [automation/README.md](../automation/README.md).
