# EMI Calculator Automation

End-to-end test automation for [emicalculator.net](https://emicalculator.net/) using **pytest**, **Playwright**, and a Page Object Model. The suite validates EMI calculation accuracy, payment schedule consistency, and Excel export parity against on-screen results.

**Target application:** Home Loan tab (primary scope)  
**Reference test plan:** `../EMI_Calculator_Test_Cases.txt`, `../EMI_Calculator_Test_Plan.txt`

---

## Table of Contents

1. [Architecture](#architecture)
2. [Regression Strategy](#regression-strategy)
3. [Execution Steps](#execution-steps)
4. [Project Structure](#project-structure)
5. [Test Coverage](#test-coverage)
6. [Configuration](#configuration)
7. [Reporting](#reporting)
8. [Troubleshooting](#troubleshooting)
9. [Future Roadmap](#future-roadmap)

---

## Architecture

The framework follows a layered design: **tests → page objects → validators/helpers → browser**.

```
┌─────────────────────────────────────────────────────────────┐
│  tests/          Class-based pytest tests (E2E flows)       │
├─────────────────────────────────────────────────────────────┤
│  pages/          Page Object Model (locators + actions)     │
├─────────────────────────────────────────────────────────────┤
│  validators/     Assertion helpers (formula, schedule, Excel)│
│  utils/          EMI oracle, currency parsing, test data    │
├─────────────────────────────────────────────────────────────┤
│  conftest.py     Fixtures, browser setup, HTML screenshots  │
│  config/         Base URL, tolerances, slider ranges        │
│  testdata/       JSON test cases                            │
└─────────────────────────────────────────────────────────────┘
```

### Layer responsibilities

| Layer | Role |
|---|---|
| **`tests/`** | Orchestrates user flows; logs steps; calls page methods and validators |
| **`pages/`** | Encapsulates UI interaction — sliders, result reading, schedule/chart/Excel |
| **`validators/`** | Pure assertion functions comparing displayed vs expected values |
| **`utils/helpers.py`** | **Calculation oracle** — independent EMI formula used as expected values |
| **`conftest.py`** | Browser lifecycle, `app_page` fixture, screenshot hook for HTML report |
| **`testdata/`** | Externalized inputs (principal, rate, tenure) keyed by test case ID |

### Key design decisions

- **E2E-first:** Calculation checks run in the browser against the live site, not as isolated unit tests.
- **Formula oracle:** `calculate_totals()` mirrors the site's rounding rules (round EMI, then derive totals).
- **Plain dicts + functions:** No dataclasses; validators are simple functions over dicts.
- **Sliders for smoke:** Inputs are set via jQuery UI slider drag to exercise the real UI path.
- **Tolerance:** ±₹1 per displayed rupee value (`EMI_TOLERANCE` in `config/settings.py`).

### Calculation oracle

The site uses the standard amortizing loan formula:

```
EMI = P × r × (1 + r)^n / ((1 + r)^n − 1)
```

Where `P` = principal, `r` = annual rate / 12 / 100, `n` = tenure in months.

Rounding matches the site:

- EMI → `round(exact_emi)`
- Total payment → `round(exact_emi × n)`
- Total interest → total payment − principal

Implementation: `utils/helpers.py` → `calculate_totals()`

### Browser setup

Configured in `conftest.py` and `pytest.ini`:

- **Chromium**, headed mode (`--headed`)
- Maximized window (`--start-maximized`, `no_viewport: True`)
- Downloads enabled (`accept_downloads: True`) for Excel export tests
- Base URL from `config/appconfig.ini`

---

## Regression Strategy

Tests are grouped by marker and run at different times based on risk and speed.

| Tier | Marker | What it checks | When to run |
|---|---|---|---|
| Smoke | `@pytest.mark.smoke` | Sliders → EMI/totals vs formula (TC-SMK-01) | Every commit / PR — `pytest -m smoke` |
| Schedule | `@pytest.mark.schedule` | Chart vs table, calendar + financial year (TC-FN-09) | Nightly — `pytest -m "smoke or schedule"` |
| Export | `@pytest.mark.export` | Excel download matches on-screen values (TC-FN-10) | Pre-release — `pytest` |

**Planned next:** parametrized calc regression (TC-CALC-01…07), Personal/Car Loan tabs, PDF and share-link tests.

---

## Execution Steps

### Prerequisites

- Python 3.10+
- Network access to `https://emicalculator.net/`

### 1. Clone and enter the project

```bash
cd emi-automation
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Run tests

**Full suite (4 tests, headed browser):**

```bash
pytest
```

**Smoke only:**

```bash
pytest -m smoke
```

**Schedule tests:**

```bash
pytest -m schedule
```

**Excel export:**

```bash
pytest -m export
```

**Headless (CI-friendly):**

```bash
pytest --headed=false
```

**Single test file:**

```bash
pytest tests/test_excel_export.py -v
```

### 5. View results

After each run:

| Output | Location |
|---|---|
| HTML report (self-contained) | `reports/report.html` |
| Per-test screenshots | `reports/{test_name}_{passed\|failed}.png` |

Open the HTML report in a browser — screenshots are embedded for every test (pass and fail).

The `reports/` folder is **cleared automatically** at the start of each run (`pytest_sessionstart` in `conftest.py`).

### 6. Override environment (optional)

```bash
TEST_ENV=prod pytest
```

Environment URLs are defined in `config/appconfig.ini`.

---

## Project Structure

```
emi-automation/
├── config/
│   ├── appconfig.ini          # Environment base URLs
│   └── settings.py            # Tolerance, timeouts, slider min/max
├── conftest.py                # Fixtures, report cleanup, screenshot hook
├── pytest.ini                 # Markers, headed mode, HTML report defaults
├── requirements.txt
├── pages/
│   ├── driver_setup.py        # Playwright page wrapper
│   ├── base_page.py           # Shared helpers + slider drag logic
│   └── emi_calculator_page.py # Home Loan PO: inputs, results, schedule, Excel
├── utils/
│   └── helpers.py             # EMI formula, parse_currency, parse_excel_export
├── validators/
│   └── results.py             # assert_emi_matches_formula, schedule, Excel checks
├── testdata/
│   └── test_cases.json        # TC-SMK-01, TC-FN-09 reference data
├── tests/
│   ├── test_home_loan_slider.py
│   ├── test_payment_schedule.py
│   └── test_excel_export.py
└── reports/                   # Generated each run (gitignored recommended)
    ├── report.html
    └── *_passed.png / *_failed.png
```

---

## Test Coverage

| # | Test class | Marker | Test case | What it checks |
|---|---|---|---|---|
| 1 | `TestHomeLoanSlider` | smoke | TC-SMK-01 | Sliders → EMI/totals vs formula |
| 2–3 | `TestPaymentSchedule` | schedule | TC-FN-09 | Chart vs table (calendar + financial year) |
| 4 | `TestExcelExport` | export | TC-FN-10 | Download Excel → match screen + schedule |

**Shared test data:** ₹10,00,000 · 10.5% · 10 years (Home Loan)

**Expected reference values (TC-CALC-01):**

| Field | Expected |
|---|---|
| EMI | ₹13,493 |
| Total interest | ₹6,19,220 |
| Total payment | ₹16,19,220 |

---

## Configuration

### `config/appconfig.ini`

```ini
[env]
active = prod

[prod]
base_url = https://emicalculator.net/
```

### `config/settings.py`

| Setting | Default | Purpose |
|---|---|---|
| `EMI_TOLERANCE` | 1 | ±₹1 per compared value |
| `RECALC_WAIT_MS` | 400 | Wait after slider change |
| `DEFAULT_TIMEOUT_MS` | 10000 | Playwright element timeout |
| `AMOUNT_MIN/MAX` | 0 / 2,00,00,000 | Home Loan amount slider range |
| `RATE_MIN/MAX` | 5.0 / 20.0 | Interest rate slider range |
| `TENURE_YEARS_MIN/MAX` | 0 / 30 | Tenure slider range |

### `pytest.ini` markers

```ini
smoke     # core slider + formula checks
schedule  # payment schedule chart vs table validation
export    # PDF/Excel export validation
```

Disabled plugins (known teardown conflicts): `html-reporter`, `reportportal`, `browserstack_sdk`.

---

## Reporting

- **pytest-html** generates `reports/report.html` with embedded base64 screenshots.
- **pytest hook** `pytest_runtest_makereport` captures a screenshot after every test (pass or fail).
- **Terminal logging** (`log_cli = true`) prints step-by-step INFO logs during execution.

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `Executable doesn't exist` (Playwright) | Run `playwright install chromium` |
| Exit code 1 after all tests pass | Global `pytest-html-reporter` plugin conflict — already disabled via `-p no:html-reporter` in `pytest.ini` |
| Slider sets approximate value | Expected for drag-based input; smoke test uses ±₹1 tolerance. For exact regression, use typed input (future). |
| Excel download fails | Ensure `accept_downloads: True` in `conftest.py` and scroll to download section before click |

---

## Future Roadmap

- [ ] Parametrized `calc_regression` over TC-CALC-01…07 (20+ datasets)
- [ ] `@pytest.mark.calc_regression` for nightly runs
- [ ] Typed-input page method for precise principal/rate/tenure
- [ ] Personal Loan and Car Loan tab coverage
- [ ] PDF export test (TC-FN-10)
- [ ] Share-link pre-fill test (TC-FN-11)
- [ ] CI pipeline (smoke on PR, full suite nightly)

---

## Related Documents

- `../EMI_Calculator_Test_Cases.txt` — detailed manual test cases
- `../EMI_Calculator_Test_Plan.txt` — strategy, formula reference, TC-CALC matrix
