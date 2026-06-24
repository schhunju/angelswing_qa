# Test Plan — EMI Calculator

| Field | Details |
|---|---|
| **Application Under Test** | [EMI Calculator](https://emicalculator.net/) |
| **Version** | Production (as of June 2026) |
| **Prepared By** | QA Team |
| **Date** | June 23, 2026 |
| **Document Status** | Draft |

---

## 1. Introduction

This document defines the test plan for the **EMI Calculator** hosted at [emicalculator.net](https://emicalculator.net/). The calculator helps users compute Equated Monthly Installments (EMI) for **Home Loan**, **Personal Loan**, and **Car Loan** in India. It provides instant results, a principal vs. interest pie chart, payment schedule tables, and export/share options.

---

## 2. Scope

### 2.1 In Scope

| Area | Description |
|---|---|
| Loan type tabs | Home Loan, Personal Loan, Car Loan |
| Input controls | Loan amount, interest rate, loan tenure (sliders + text fields) |
| Tenure unit toggle | Years (`Yr`) / Months (`Mo`) |
| EMI scheme | EMI in Advance / EMI in Arrears (Car Loan) |
| Output calculations | Loan EMI, Total Interest Payable, Total Payment |
| Visual output | Pie chart — break-up of total payment (Principal vs. Interest %) |
| Payment schedule | Calendar Year wise / Financial Year wise views |
| Export & share | Download PDF, Download Excel, Share link (pre-filled URL) |
| Input synchronization | Slider ↔ text field sync |
| Cross-browser & responsive | Desktop and mobile layouts |
| Accessibility | Keyboard navigation, labels, readable contrast |

### 2.2 Out of Scope

- Third-party articles, blog posts, and comment sections
- Android app (separate product)
- Home Loan EMI Calculator with Prepayments (separate page)
- Credit Card EMI Calculator (separate page)
- Backend/server infrastructure testing
- Performance/load testing beyond basic page load

---

## 3. Test Objectives

1. Verify EMI, total interest, and total payment are **mathematically correct** for all loan types.
2. Confirm all input controls update results **instantly and consistently**.
3. Validate **boundary values** and invalid inputs are handled gracefully.
4. Ensure **UI/UX** behavior (tabs, toggles, sliders, charts) works across browsers and devices.
5. Verify **export/share** features produce accurate, usable outputs.
6. Confirm **payment schedule** data aligns with calculated EMI values.

---

## 4. Reference — EMI Formula

The application uses the standard amortizing loan EMI formula:

```
EMI = P × r × (1 + r)^n / ((1 + r)^n − 1)
```

Where:

| Symbol | Meaning |
|---|---|
| **E** | EMI (monthly payment) |
| **P** | Principal loan amount (₹) |
| **r** | Monthly interest rate = Annual Rate / 12 / 100 |
| **n** | Loan tenure in **months** |

**Derived values:**

- Total Payment = EMI × n  
- Total Interest = Total Payment − P  

**Official example** (from site documentation):

| Input | Value |
|---|---|
| Principal | ₹10,00,000 |
| Rate | 10.5% p.a. |
| Tenure | 10 years (120 months) |
| **Expected EMI** | **₹13,493** |
| **Expected Total Payment** | **₹16,19,220** |
| **Expected Total Interest** | **₹6,19,220** |

**Screenshot reference values** (Home Loan):

| Input | Value |
|---|---|
| Principal | ₹50,00,000 |
| Rate | 9% p.a. |
| Tenure | 20 years |
| **Expected EMI** | **₹44,986** |
| **Expected Total Interest** | **₹57,96,711** |
| **Expected Total Payment** | **₹1,07,96,711** |
| **Pie chart** | Principal ~46.3%, Interest ~53.7% |

---

## 5. Test Strategy

| Test Type | Approach |
|---|---|
| **Functional** | Manual + automated (Selenium/Playwright) for calculation regression |
| **Calculation accuracy** | Compare outputs against formula (Excel/script) for 20+ data sets |
| **Boundary value analysis** | Min, max, and edge values for each input |
| **Equivalence partitioning** | Valid/invalid ranges for amount, rate, tenure |
| **UI/UX** | Visual inspection, slider sync, tab switching |
| **Compatibility** | Chrome, Firefox, Safari, Edge; iOS/Android mobile browsers |
| **Regression** | Re-run core calculation suite after any site update |

---

## 6. Test Environment

| Component | Requirement |
|---|---|
| **URL** | https://emicalculator.net/ |
| **Browsers** | Chrome (latest), Firefox (latest), Safari (latest), Edge (latest) |
| **Devices** | Desktop (1920×1080), Tablet (768×1024), Mobile (375×667) |
| **OS** | Windows 11, macOS, Android 14+, iOS 17+ |
| **Network** | Standard broadband; optional slow-3G for load behavior |
| **Tools** | Browser DevTools, Excel (verification), optional automation framework |

---

## 7. Entry & Exit Criteria

### 7.1 Entry Criteria

- Test environment is accessible
- Test plan reviewed and approved
- Reference calculation spreadsheet/script prepared
- Test data sets documented

### 7.2 Exit Criteria

- All **P0/P1** test cases executed with ≥ 95% pass rate
- **Zero open P0 defects**; P1 defects documented with workaround or fix plan
- Calculation accuracy validated for all loan types
- Test summary report delivered

---

## 8. Test Cases

### 8.1 Loan Type Tabs

| TC ID | Test Case | Steps | Expected Result | Priority |
|---|---|---|---|---|
| TC-TAB-01 | Default tab on page load | Open homepage | **Home Loan** tab is active; Home Loan labels/defaults shown | P0 |
| TC-TAB-02 | Switch to Personal Loan | Click **Personal Loan** tab | Tab activates; inputs/defaults update for personal loan | P0 |
| TC-TAB-03 | Switch to Car Loan | Click **Car Loan** tab | Tab activates; **EMI Scheme** (Advance/Arrears) section visible | P0 |
| TC-TAB-04 | Tab state persistence | Switch tabs, adjust values, switch back | Each tab retains its last-used values (if applicable) or resets per design | P1 |
| TC-TAB-05 | Visual active state | Click each tab | Active tab has distinct styling; inactive tabs are visually distinct | P2 |

---

### 8.2 Loan Amount Input

| TC ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| TC-AMT-01 | Default amount display | Load page (Home Loan) | Amount field shows formatted value with ₹ symbol | P1 |
| TC-AMT-02 | Slider min boundary | Set slider to **0** | Amount = 0; EMI/interest reflect zero or appropriate message | P0 |
| TC-AMT-03 | Slider max boundary | Set slider to **200L** (₹2,00,00,000) | Amount updates; EMI calculated correctly | P0 |
| TC-AMT-04 | Mid-range via slider | Set to **50L** | Field shows `50,00,000`; EMI recalculates | P0 |
| TC-AMT-05 | Manual text entry | Type `2500000` and tab out | Field formats to `25,00,000`; slider syncs; EMI updates | P0 |
| TC-AMT-06 | Slider ↔ field sync | Move slider, then edit field | Both controls stay in sync bidirectionally | P0 |
| TC-AMT-07 | Invalid text input | Enter letters/special chars | Input rejected or sanitized; no crash | P1 |
| TC-AMT-08 | Amount exceeds max | Enter value > 200L manually | Clamped to max or error shown | P1 |

**Slider tick marks (Home Loan):** 0, 25L, 50L, 75L, 100L, 125L, 150L, 175L, 200L

---

### 8.3 Interest Rate Input

| TC ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| TC-INT-01 | Default rate | Load page | Rate displays with `%` suffix | P1 |
| TC-INT-02 | Min boundary | Set rate to **5%** | EMI recalculates correctly | P0 |
| TC-INT-03 | Max boundary | Set rate to **20%** | EMI recalculates correctly | P0 |
| TC-INT-04 | Mid-range | Set rate to **9%** | Matches reference: EMI ₹44,986 (for ₹50L / 20 Yr) | P0 |
| TC-INT-05 | Decimal rate | Enter **10.5%** | Matches official example EMI ₹13,493 (₹10L / 10 Yr) | P0 |
| TC-INT-06 | Slider ↔ field sync | Adjust via slider and typing | Values stay synchronized | P0 |
| TC-INT-07 | Zero interest rate | Enter **0%** | EMI = P/n (or handled per business rule); no error | P1 |
| TC-INT-08 | Out-of-range rate | Enter **25%** | Clamped or validation message shown | P1 |

**Slider tick marks:** 5, 7.5, 10, 12.5, 15, 17.5, 20

---

### 8.4 Loan Tenure Input

| TC ID | Test Case | Input | Expected Result | Priority |
|---|---|---|---|---|
| TC-TEN-01 | Default tenure | Load page | Tenure shown in **Yr** mode | P1 |
| TC-TEN-02 | Min boundary (years) | Set to **0** years | Handled gracefully (EMI = 0 or validation) | P0 |
| TC-TEN-03 | Max boundary (years) | Set to **30** years | EMI recalculates; n = 360 months | P0 |
| TC-TEN-04 | Toggle Yr → Mo | 20 Yr → switch to **Mo** | Value converts to **240** months; EMI unchanged | P0 |
| TC-TEN-05 | Toggle Mo → Yr | 240 Mo → switch to **Yr** | Value converts to **20** years; EMI unchanged | P0 |
| TC-TEN-06 | Tenure in months directly | Set **120** Mo at 10.5%, ₹10L | EMI = ₹13,493 | P0 |
| TC-TEN-07 | Slider ↔ field sync | Adjust slider and type value | Synchronized correctly | P0 |
| TC-TEN-08 | Active toggle styling | Click Yr / Mo | Selected unit highlighted (blue-gray active state) | P2 |

**Slider tick marks (years):** 0, 5, 10, 15, 20, 25, 30

---

### 8.5 EMI Calculation — Core Scenarios

| TC ID | Loan Type | Principal | Rate | Tenure | Expected EMI | Expected Total Interest | Expected Total Payment | Priority |
|---|---|---|---|---|---|---|---|---|
| TC-CALC-01 | Home | ₹10,00,000 | 10.5% | 10 Yr | ₹13,493 | ₹6,19,220 | ₹16,19,220 | P0 |
| TC-CALC-02 | Home | ₹50,00,000 | 9% | 20 Yr | ₹44,986 | ₹57,96,711 | ₹1,07,96,711 | P0 |
| TC-CALC-03 | Home | ₹25,00,000 | 7.5% | 15 Yr | Verify via formula | Verify via formula | Verify via formula | P0 |
| TC-CALC-04 | Personal | ₹5,00,000 | 12% | 5 Yr | Verify via formula | Verify via formula | Verify via formula | P0 |
| TC-CALC-05 | Car | ₹8,00,000 | 9.5% | 7 Yr | Verify via formula | Verify via formula | Verify via formula | P0 |
| TC-CALC-06 | Home | ₹1,00,00,000 | 8% | 25 Yr | Verify via formula | Verify via formula | Verify via formula | P1 |
| TC-CALC-07 | Home | ₹1,00,000 | 15% | 1 Yr | Verify via formula | Verify via formula | Verify via formula | P1 |
| TC-CALC-08 | Any | Change any input | — | Results update **without page reload** | P0 |

**Verification method:** Automate formula in Excel/Python; allow ±₹1 rounding tolerance per displayed value.

---

### 8.6 EMI Scheme (Car Loan)

| TC ID | Test Case | Steps | Expected Result | Priority |
|---|---|---|---|---|
| TC-SCH-01 | Scheme visibility | Open Home/Personal Loan tabs | EMI Scheme section **not shown** (or disabled) | P1 |
| TC-SCH-02 | Scheme visibility | Open Car Loan tab | **EMI in Advance** and **EMI in Arrears** options visible | P0 |
| TC-SCH-03 | EMI in Arrears (default) | Select Arrears; note EMI | Standard EMI formula applied | P0 |
| TC-SCH-04 | EMI in Advance | Select Advance; same inputs | EMI differs from Arrears (advance formula); recalculates instantly | P0 |
| TC-SCH-05 | Switch scheme mid-session | Toggle Advance ↔ Arrears | All outputs and chart update accordingly | P1 |

---

### 8.7 Output Display & Pie Chart

| TC ID | Test Case | Steps | Expected Result | Priority |
|---|---|---|---|---|
| TC-OUT-01 | EMI formatting | Set known inputs | EMI shown as `₹ XX,XXX` with Indian numbering | P0 |
| TC-OUT-02 | Total interest formatting | Set known inputs | Formatted with ₹ and comma separators | P1 |
| TC-OUT-03 | Total payment = EMI × n | Verify for TC-CALC-01 | ₹13,493 × 120 = ₹16,19,160 (± rounding) | P0 |
| TC-OUT-04 | Pie chart renders | Set any valid inputs | Chart visible with Principal (green) and Interest (orange) segments | P1 |
| TC-OUT-05 | Pie chart percentages | TC-CALC-02 values | Principal ~46.3%, Interest ~53.7% | P1 |
| TC-OUT-06 | Percentages sum to 100% | Any valid input set | Principal % + Interest % = 100% | P1 |
| TC-OUT-07 | Chart updates on input change | Change rate slider | Chart segments and percentages update in real time | P1 |
| TC-OUT-08 | Legend labels | Inspect chart | Green = Principal, Orange = Total Interest | P2 |

---

### 8.8 Payment Schedule

| TC ID | Test Case | Steps | Expected Result | Priority |
|---|---|---|---|---|
| TC-SCHD-01 | Schedule section visible | Scroll below results | Payment schedule table/chart displayed | P1 |
| TC-SCHD-02 | Calendar Year wise | Select **Calendar Year wise** | Schedule grouped by calendar year | P1 |
| TC-SCHD-03 | Financial Year wise | Select **Financial Year wise** | Schedule grouped by FY (Apr–Mar) | P1 |
| TC-SCHD-04 | Schedule start date | Verify "Schedule showing EMI payments starting from" | Correct start year/month based on inputs | P2 |
| TC-SCHD-05 | Principal + interest per period | Inspect first year | Interest portion > principal in early years | P1 |
| TC-SCHD-06 | Schedule totals match | Sum schedule rows | Total matches Total Payment output (± rounding) | P0 |
| TC-SCHD-07 | Schedule updates | Change tenure | Row count and totals update accordingly | P1 |

---

### 8.9 Export & Share

| TC ID | Test Case | Steps | Expected Result | Priority |
|---|---|---|---|---|
| TC-EXP-01 | Download PDF | Set inputs → click **Download PDF** | PDF downloads; contains correct EMI, inputs, and schedule | P1 |
| TC-EXP-02 | Download Excel | Click **Download Excel** | Excel file downloads; values match on-screen results | P1 |
| TC-EXP-03 | Share link generation | Click **Share** / copy link | URL contains pre-filled query parameters | P1 |
| TC-EXP-04 | Shared link pre-fill | Open copied URL in new tab/incognito | All inputs and results pre-populated correctly | P0 |
| TC-EXP-05 | Share link after input change | Modify values → copy new link | New link reflects updated values | P1 |

---

### 8.10 UI/UX & Responsiveness

| TC ID | Test Case | Steps | Expected Result | Priority |
|---|---|---|---|---|
| TC-UI-01 | Page load time | Open URL | Page loads within 3 seconds on broadband | P2 |
| TC-UI-02 | Mobile layout | Open on 375px viewport | All controls usable; no horizontal overflow | P1 |
| TC-UI-03 | Tablet layout | Open on 768px viewport | Layout adapts; chart and inputs visible | P2 |
| TC-UI-04 | Keyboard navigation | Tab through inputs | Focus order logical; values editable via keyboard | P2 |
| TC-UI-05 | Slider drag interaction | Drag each slider | Smooth movement; value updates continuously | P1 |
| TC-UI-06 | No layout shift on recalc | Change inputs rapidly | Output section does not jump or flicker excessively | P2 |

---

### 8.11 Cross-Browser Compatibility

| TC ID | Browser | Core Tests to Run | Priority |
|---|---|---|---|
| TC-XB-01 | Chrome (latest) | TC-CALC-01, TC-CALC-02, TC-TAB-01–03, TC-EXP-04 | P0 |
| TC-XB-02 | Firefox (latest) | TC-CALC-01, TC-CALC-02, TC-TAB-01–03 | P1 |
| TC-XB-03 | Safari (latest) | TC-CALC-01, TC-CALC-02, TC-TAB-01–03 | P1 |
| TC-XB-04 | Edge (latest) | TC-CALC-01, TC-CALC-02 | P1 |
| TC-XB-05 | Mobile Safari (iOS) | TC-CALC-02, TC-UI-02 | P1 |
| TC-XB-06 | Chrome (Android) | TC-CALC-02, TC-UI-02 | P1 |

---

### 8.12 Negative & Edge Cases

| TC ID | Test Case | Input / Action | Expected Result | Priority |
|---|---|---|---|---|
| TC-NEG-01 | All inputs at minimum | ₹0, 5%, 0 Yr | Graceful handling; no JS errors in console | P0 |
| TC-NEG-02 | All inputs at maximum | 200L, 20%, 30 Yr | Valid calculation; no overflow/display issues | P0 |
| TC-NEG-03 | Very short tenure | ₹10L, 10%, 1 Mo | EMI calculated for 1 month | P1 |
| TC-NEG-04 | Paste formatted number | Paste `50,00,000` into amount field | Parsed correctly | P1 |
| TC-NEG-05 | Empty field | Clear amount field and tab out | Defaults restored or validation shown | P1 |
| TC-NEG-06 | Rapid input changes | Drag all sliders quickly | Final displayed values are consistent; no stale results | P1 |
| TC-NEG-07 | Browser back/forward | Navigate away and return | Page reloads with default or cached state per design | P2 |

---

## 9. Test Data Summary

### 9.1 Primary Regression Data Set

```
| # | Tab        | Amount (₹)  | Rate (%) | Tenure   | Notes                    |
|---|------------|-------------|----------|----------|--------------------------|
| 1 | Home       | 10,00,000   | 10.5     | 10 Yr    | Official site example    |
| 2 | Home       | 50,00,000   | 9        | 20 Yr    | Screenshot reference     |
| 3 | Home       | 25,00,000   | 7.5      | 15 Yr    | Mid-range                |
| 4 | Personal   | 5,00,000    | 12       | 5 Yr     | Short-term personal loan |
| 5 | Car        | 8,00,000    | 9.5      | 7 Yr     | Car loan + EMI scheme    |
| 6 | Home       | 1,00,00,000 | 8        | 25 Yr    | High principal           |
| 7 | Home       | 1,00,000    | 15       | 1 Yr     | Low principal            |
| 8 | Home       | 50,00,000   | 9        | 240 Mo   | Tenure in months         |
```

### 9.2 Boundary Data Set

```
| Input          | Min    | Max      |
|----------------|--------|----------|
| Loan Amount    | ₹0     | ₹2 Cr    |
| Interest Rate  | 5%     | 20%      |
| Tenure (Years) | 0      | 30       |
| Tenure (Months)| 0      | 360      |
```

---

## 10. Defect Severity Guidelines

| Severity | Definition | Example |
|---|---|---|
| **P0 — Critical** | Wrong EMI/calculation; app crash; data loss on share | EMI off by > ₹100 for standard inputs |
| **P1 — High** | Feature broken; incorrect schedule totals; export wrong values | PDF shows different EMI than screen |
| **P2 — Medium** | UI glitch; minor formatting; non-critical sync delay | Comma formatting inconsistent |
| **P3 — Low** | Cosmetic; typo; minor alignment on one browser | Legend text misaligned on Safari |

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Rounding differences vs. manual calc | False failures | Define ±₹1 tolerance; use same rounding as app |
| Third-party CDN/chart library failure | Chart not rendered | Test with DevTools offline simulation; verify numeric outputs still correct |
| Shared link parameter format changes | Broken deep links | Maintain URL parameter regression tests |
| Mobile slider precision | Hard to set exact values | Supplement with direct text entry tests |
| Car Loan Advance vs. Arrears formula undocumented | Incorrect expected values | Derive expected values from financial literature; confirm with 2+ reference sources |

---

## 12. Deliverables

| # | Deliverable | Owner |
|---|---|---|
| 1 | This Test Plan | QA Lead |
| 2 | Test Cases (detailed steps in test management tool) | QA Engineer |
| 3 | Calculation verification spreadsheet/script | QA Engineer |
| 4 | Test Execution Report | QA Engineer |
| 5 | Defect Log | QA Engineer |
| 6 | Test Summary & Sign-off | QA Lead |

---

## 13. Schedule (Suggested)

| Phase | Duration | Activities |
|---|---|---|
| Test design | 1 day | Finalize cases, build verification script |
| Functional testing | 2 days | Execute TC 8.1 – 8.9 |
| Compatibility testing | 1 day | Execute TC 8.11 |
| Regression & retest | 1 day | Re-run failed cases after fixes |
| Reporting | 0.5 day | Summary report and sign-off |

**Total estimated effort:** ~5.5 person-days

---

## 14. Approvals

| Role | Name | Signature | Date |
|---|---|---|---|
| QA Lead | | | |
| Project Manager | | | |
| Development Lead | | | |

---

*End of Test Plan*
