# Test strategy

Companion to [bug-reports.md](bug-reports.md) and [test-plan.md](test-plan.md). Severities and evidence live in the bug doc; this is triage order and where automation stops.

## Focus

- Money path: balance, stake rules, amounts shown vs API (**BUG-002**, **BUG-004**, **BUG-006**, **BUG-007**).
- UX vs brief: slip, filters, modals, receipt (**BUG-001**, **BUG-003**, **BUG-005**).
- Automation: two Pytest/Playwright tests in [`automation/tests/test_betting.py`](../automation/tests/test_betting.py). Everything else is manual or Postman per the test plan.

## Risk (from the bug log)

| Area | Bug | Coverage |
|------|-----|----------|
| Balance / overdraft | **BUG-004** | Bug report steps; happy-path test only checks balance after a valid bet |
| Payout wrong on receipt | **BUG-006** | Manual / Pytest/Playwright in bug report; automation checks modal payout shape, not slip vs modal |
| Currency in JSON | **BUG-002** | Postman in bug report |
| Filter count vs list | **BUG-001** | TC-05 manual |
| Receipt missing Selection | **BUG-003** | Manual |
| Escape and modals | **BUG-005** | Pytest/Playwright in bug report |
| API vs OpenAPI | **BUG-002**, **BUG-004**, TC-06 | Postman |
| Header vs API after reset | **BUG-007** | Manual browser + Postman |

## Automation scope

- `conftest.py` calls `POST /api/reset-balance` before each test.
- `GET /api/matches` provides `matchId` and odds (nothing hard-coded from a static catalogue).

The brief asked for a small automated set: one successful placement (receipt + balance) and one stake validation (below minimum in the UI). Filters, failure modal flows, full stake matrix, and API negatives stay in the test plan and bug log; Postman is enough for TC-06.

## Recommendations (beyond the logged bugs)

These are proactive product/engineering ideas. They do not replace fixes in [bug-reports.md](bug-reports.md); they reduce risk as the list grows or traffic increases.

| Topic | Recommendation |
|--------|----------------|
| **Accessibility (ARIA)** | Treat success and error surfaces as real dialogs: keep `role="dialog"` where appropriate, set `aria-modal="true"`, tie the visible title to **`aria-labelledby`** (and optional **`aria-describedby`** for the main message). On open, move **focus** into the dialog; on close, return focus to the control that opened it. Announces intent for screen readers and pairs with **BUG-005** (Escape). |
| **Match list scale** | For large catalogs, add **pagination** or **virtualized scrolling** with a clear “showing X–Y of Z” pattern (and sync with filters so the count stays honest; see **BUG-001**). Improves performance and keyboard reachability. |
| **Long page UX** | Add a **back to top** control after long scroll through matches/filters so users are not stranded at the bottom. |
| **Success receipt — bet type** | After place, the modal should show **which side was bet** (**HOME**, **DRAW**, or **AWAY**) — same idea as **Selection** in FR 2.4. Today the slip has the pick but the receipt has no dedicated line; see **BUG-003** and the **BUG-003** row under *Product notes* below. |

## Suggested fix order

By severity in [bug-reports.md](bug-reports.md); product can reprioritize.

1. **BUG-004** — Critical: negative balance.
2. **BUG-006** — Major: receipt payout vs slip / API.
3. **BUG-001**, **BUG-007** — Major: filter count; header balance vs reset/API.
4. **BUG-002**, **BUG-003**, **BUG-005** — Minor: currency field, Selection row, Escape.

## Product notes (from suggested fixes in the bug doc)

| Bug | Direction |
|-----|-----------|
| BUG-001 | Drive `#match-list-count` from the filtered list. |
| BUG-002 | Same `currency` (EUR) on `place-bet`, `balance`, `reset-balance`. |
| BUG-003 | Add Selection on the receipt or align the spec. |
| BUG-004 | Reject stake above balance server-side; no negative balance. |
| BUG-005 | Close modals on Escape (or document otherwise) and match focus behavior. |
| BUG-006 | Align `#modal-success-payout` with slip and `place-bet` `payout`. |
| BUG-007 | Refetch `GET /api/balance` for the header; fix persistence if GET and reset disagree. |

## Later automation (if the team expands this repo)

- Assert slip `#bet-slip-potential-payout` equals `#modal-success-payout` before close (**BUG-006**).
- Escape closes modal (**BUG-005**).
- Mock failed `place-bet` for error modal copy and buttons (TC-03).
- Small API test module or exported Postman collection for TC-06.
