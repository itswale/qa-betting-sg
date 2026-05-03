# Bug reports

Manual and API checks against the hosted app.

**App:** `https://qae-assignment-tau.vercel.app`  
**Sample user:** `candidate-Z1tPv7cRx5K` (use in `?user-id=` and header `x-user-id`)  
**Updated:** 2026-05-02  

BUG-002–006: verified on that host(browser where noted). BUG-007: browser + Postman with the same user id. BUG-001 is UI-only.

### Postman — setup (do this for every API request)

1. Open Postman → **New** → **HTTP Request** (or duplicate an existing tab).
2. Set the **method** (GET / POST) from the dropdown.
3. Paste the **full URL** from the bug steps (host is always `https://qae-assignment-tau.vercel.app` unless you are on another deploy).
4. Open the **Headers** tab → add key `x-user-id`, value your user string (must match `?user-id=` in the browser when you compare to the UI). Leave it off only when a bug step says to test “missing header”.
5. For POSTs with a body: **Body** → **raw** → choose **JSON** from the dropdown → paste the JSON. Do not send a body on `reset-balance`.
6. Click **Send**. Read **Status** and the **Body** tab (Pretty JSON).

**Quick reference**

| Method | Full path (append to host) | Body |
|--------|----------------------------|------|
| GET | `/api/matches` | none |
| GET | `/api/balance` | none |
| POST | `/api/reset-balance` | none |
| POST | `/api/place-bet` | JSON: `matchId`, `selection` (`HOME` / `DRAW` / `AWAY`), `stake` |

Host + path examples: `https://qae-assignment-tau.vercel.app/api/balance`, `https://qae-assignment-tau.vercel.app/api/place-bet`.

---

## BUG-001 — “Showing … matches” ignores filters

| Field | Value |
|--------|--------|
| **Severity** | Major |
| **Where** | Match list + filters |
| **Assignment** | FR 2.6 |

**Steps**  
Open app → read `#match-list-count` → apply date or odds filter that removes many rows → compare count to rows shown.

**Expected**  
Count matches filtered list.

**Actual**  
Count can stay at the old total while the list shrinks.

**Evidence**  
Manual on live URL; optional DOM capture via devtools or `automation/` pytest with `PWDEBUG=1`.<img width="1393" height="414" alt="Screenshot 2026-05-03 at 3 01 32 PM" src="https://github.com/user-attachments/assets/19a23511-b49d-4cf4-bde7-e79538871143" />


**Suggested fix**  
Bind `#match-list-count` to the same filtered data as the cards.

---

## BUG-002 — `place-bet` currency vs other endpoints

| Field | Value |
|--------|--------|
| **Severity** | Minor |
| **Where** | `POST /api/place-bet` vs `GET /api/balance`, `POST /api/reset-balance` |

**Postman — step by step**

1. **Reset (optional, clean wallet):** POST `https://qae-assignment-tau.vercel.app/api/reset-balance` → Headers: `x-user-id` = `candidate-Z1tPv7cRx5K` (or your id) → no Body → Send → **200**, note `currency` in JSON (expect EUR).
2. **Balance check:** GET `https://qae-assignment-tau.vercel.app/api/balance` → same `x-user-id` header → Send → **200**, note `currency` (expect EUR).
3. **Place bet:** POST `https://qae-assignment-tau.vercel.app/api/place-bet` → same `x-user-id` → Body raw JSON:
   ```json
   {"matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":10}
   ```
   → Send → **200** → read the `currency` field in the response body.

**Expected**  
EUR everywhere per brief.

**Actual**  
Step 3 response: `"currency":"USD"`. Steps 1–2: `"currency":"EUR"`.

**Evidence**  
Same three requests in order; screenshot or copy-paste of JSON `currency` fields.
<img width="1269" height="789" alt="Screenshot 2026-05-03 at 3 09 27 PM" src="https://github.com/user-attachments/assets/faf090d9-e2de-4eca-9f6a-9119b8b0de18" />


**Suggested fix**  
Return EUR consistently on all money responses.

---

## BUG-003 — No “Selection” line on success receipt

| Field | Value |
|--------|--------|
| **Severity** | Minor |
| **Where** | Success modal |

**Assignment (FR 2.4)**  
Receipt should list Selection (HOME / DRAW / AWAY) with bet id, match, stake, odds, payout, time.

**Actual**  
Client exposes ids like `modal-success-bet-id`, `modal-success-match`, … but not `modal-success-selection`. Selection only appears on the slip before place.<img width="1385" height="641" alt="Screenshot 2026-05-03 at 3 11 31 PM" src="https://github.com/user-attachments/assets/1d8f5ec7-b9bd-45dc-9d8c-097110dc6160" />

**Suggested fix**  
Add a Selection row on the receipt, or change the spec if intentional.

---

## BUG-004 — Bet accepted with insufficient balance (negative balance)

| Field | Value |
|--------|--------|
| **Severity** | Critical |
| **Where** | `POST /api/place-bet` |

Use one user id in `x-user-id` for every step (e.g. `candidate-Z1tPv7cRx5K`). Same JSON shape for each place-bet; only `stake` changes.

**Postman — step by step**

1. POST `https://qae-assignment-tau.vercel.app/api/reset-balance` — Headers: `x-user-id` — no Body — Send (**200**).
2. POST `https://qae-assignment-tau.vercel.app/api/place-bet` — Headers: `x-user-id` — Body:
   ```json
   {"matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":30}
   ```
   — Send (**200**). Repeat this request **two more times** (three stakes of 30 total).
3. GET `https://qae-assignment-tau.vercel.app/api/balance` — same header — Send (**200**). Confirm `balance` is **greater than 0** and **less than 100** (so a stake of 100 exceeds wallet but is still allowed by the €100 per-bet cap).
4. POST `https://qae-assignment-tau.vercel.app/api/place-bet` — same header — Body:
   ```json
   {"matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":100}
   ```
   — Send.

**Expected**  
**422** (or similar) and no bet; balance must not go negative.

**Actual**  
**200** on step 4; response body can show `"balance":-70`. Step 3 may still show `"balance":30` depending on timing — note both.

**Suggested fix**  
Validate stake ≤ balance before commit; clear errors; tests for the rule.

---

## BUG-005 — Escape does not close modals

| Field | Value |
|--------|--------|
| **Severity** | Minor |
| **Where** | `#modal-success`, `#modal-error` |

**Steps**  
Open success modal after a small bet → Escape. Open error modal (e.g. failed place-bet) → Escape.

**Expected**  
Escape dismisses dialog (or documented alternative).

**Actual**  
Both stay open after Escape (Pytest automation: still visible).

**Evidence**  
Escape key does notn close the dialog.

**Suggested fix**  
Wire Escape to the same close path as Close/backdrop; handle focus.

---

## BUG-006 — Success modal payout ≠ slip (and API)

| Field | Value |
|--------|--------|
| **Severity** | Major |
| **Where** | `#bet-slip-potential-payout` vs `#modal-success-payout` |

**UI (repro the visual bug)**  
Open app with `?user-id=` → pick HOME on Man Utd vs Chelsea → stake **€1.00** → read slip **Potential payout** → **Place bet** → read modal **Potential payout**.

**Postman — step by step (proves API returns correct payout)**

1. GET `https://qae-assignment-tau.vercel.app/api/matches` — Header `x-user-id` — Send — find the match with `"id":"premier-league-manutd-chelsea"` and confirm home odds **2.45** in the JSON.
2. POST `https://qae-assignment-tau.vercel.app/api/place-bet` — same header — Body:
   ```json
   {"matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":1}
   ```
   — Send — **200** — in the response, confirm `"payout":2.45` and `"odds":2.45` (values may be numbers without quotes in Pretty view).

**Expected**  
Slip and modal both show **€2.45**; Postman step 2 matches.

**Actual**  
Slip €2.45; modal €2.00; odds still 2.45 on modal; Postman shows `payout` **2.45**.

**Evidence**  
Screenshots (slip + modal) plus Postman response body for step 2.

**Suggested fix**  
Receipt payout from same source as slip / `place-bet` response; regression: slip vs modal before close.

---

## BUG-007 — Header balance ≠ API after reset (same user)

| Field | Value |
|--------|--------|
| **Severity** | Major |
| **Where** | Header vs `reset-balance` / `GET /api/balance` |

**Precondition**  
The string in the browser URL `?user-id=` must be **identical** to the `x-user-id` header on every Postman request. Otherwise you are not comparing the same account as the page.

**Browser**

1. Open `https://qae-assignment-tau.vercel.app/?user-id=candidate-Z1tPv7cRx5K`.
2. Note the balance in the **header** (example: **€120**).

**Postman — step by step**

3. POST `https://qae-assignment-tau.vercel.app/api/reset-balance` — Headers: `x-user-id` = **exactly** the same value as in step 1’s URL — no Body — Send (**200**). In the response JSON, read `balance` (example **125.5**).
4. GET `https://qae-assignment-tau.vercel.app/api/balance` — same `x-user-id` — Send (**200**). Confirm `balance` matches what you saw in step 3.

**Browser again**

5. Hard refresh the tab (full reload). Read the header balance again.

**Expected**  
Header matches steps 3–4 (same number / same rounding rule everywhere).

**Actual**  
Example: step 3–4 show **125.5**; step 5 header still **€120** after refresh.

**Evidence**  
Postman response bodies from steps 3–4 + note or screenshot of header after step 5.

**Suggested fix**  
Load header from `GET /api/balance` after navigation and after server-side balance changes. If GET disagrees with reset, fix server read/persistence first.

---

## Adding a new bug

Use the same QA Flow fiels: severity, where, expected, actual, evidence, suggested fix. For anything involving the API, add a **Postman — step by step** block (numbered: URL, method, headers, body, what to check in the response) so someone else can reproduce.
