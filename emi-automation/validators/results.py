"""Validation helpers for EMI calculator results."""

from __future__ import annotations

from config.settings import EMI_TOLERANCE
from utils.helpers import EmiTotals


def assert_emi_matches_formula(
    displayed: dict[str, int],
    expected: EmiTotals,
    principal: int,
    tenure_months: int,
    tolerance: int = EMI_TOLERANCE,
) -> None:
    """Assert displayed EMI values match formula-based expectations."""
    assert abs(displayed["emi"] - expected["emi"]) <= tolerance, (
        f"EMI mismatch: displayed {displayed['emi']}, expected {expected['emi']}"
    )
    assert abs(displayed["total_payment"] - expected["total_payment"]) <= tolerance, (
        f"Total payment mismatch: displayed {displayed['total_payment']}, "
        f"expected {expected['total_payment']}"
    )
    assert abs(displayed["total_interest"] - expected["total_interest"]) <= tolerance, (
        f"Total interest mismatch: displayed {displayed['total_interest']}, "
        f"expected {expected['total_interest']}"
    )

    cumulative_tolerance = max(tolerance, tenure_months)
    derived_total = displayed["emi"] * tenure_months
    assert abs(displayed["total_payment"] - derived_total) <= cumulative_tolerance, (
        f"Total payment != EMI × tenure: {displayed['total_payment']} vs "
        f"{displayed['emi']} × {tenure_months} = {derived_total}"
    )

    derived_interest = displayed["total_payment"] - principal
    assert abs(displayed["total_interest"] - derived_interest) <= tolerance, (
        f"Total interest != total - principal: {displayed['total_interest']} vs "
        f"{displayed['total_payment']} - {principal} = {derived_interest}"
    )


def assert_schedule_matches_chart(
    table_rows: list[dict],
    chart_rows: list[dict],
    tolerance: int = EMI_TOLERANCE,
) -> None:
    """Assert bar chart and schedule table agree year-wise."""
    assert len(table_rows) == len(chart_rows), (
        f"Row count mismatch: table={len(table_rows)}, chart={len(chart_rows)}"
    )
    assert table_rows, "No schedule rows found in table"

    for table_row, chart_row in zip(table_rows, chart_rows):
        year = table_row["year"]
        assert table_row["year"] == chart_row["year"], (
            f"Year label mismatch: table={table_row['year']}, chart={chart_row['year']}"
        )
        assert abs(table_row["principal"] - chart_row["principal"]) <= tolerance, (
            f"{year} principal mismatch: "
            f"table={table_row['principal']}, chart={chart_row['principal']}"
        )
        assert abs(table_row["interest"] - chart_row["interest"]) <= tolerance, (
            f"{year} interest mismatch: "
            f"table={table_row['interest']}, chart={chart_row['interest']}"
        )
        assert abs(table_row["balance"] - chart_row["balance"]) <= tolerance, (
            f"{year} balance mismatch: "
            f"table={table_row['balance']}, chart={chart_row['balance']}"
        )
        chart_total = chart_row["principal"] + chart_row["interest"]
        assert abs(table_row["total_payment"] - chart_total) <= tolerance, (
            f"{year} total mismatch: "
            f"table={table_row['total_payment']}, chart={chart_total}"
        )


def assert_schedule_total_matches(
    table_rows: list[dict],
    headline_total_payment: int,
    tolerance: int | None = None,
) -> None:
    """Assert summed schedule rows match headline Total Payment."""
    if tolerance is None:
        tolerance = max(EMI_TOLERANCE, len(table_rows))

    schedule_sum = sum(row["total_payment"] for row in table_rows)
    assert abs(schedule_sum - headline_total_payment) <= tolerance, (
        f"Schedule total mismatch: sum={schedule_sum}, "
        f"headline={headline_total_payment}"
    )


def assert_excel_matches_screen(
    excel: dict[str, int | float | list[dict]],
    displayed: dict[str, int],
    inputs: dict[str, int | float],
    tolerance: int = EMI_TOLERANCE,
) -> None:
    """Assert downloaded Excel summary and schedule match on-screen calculator values."""
    for field in ("emi", "total_interest", "total_payment"):
        excel_value = int(excel[field])
        assert abs(excel_value - displayed[field]) <= tolerance, (
            f"Excel {field} mismatch: excel={excel_value}, screen={displayed[field]}"
        )

    assert abs(int(excel["principal"]) - int(inputs["principal"])) <= tolerance, (
        f"Excel principal mismatch: excel={excel['principal']}, "
        f"expected={inputs['principal']}"
    )
    assert abs(float(excel["rate"]) - float(inputs["rate"])) < 0.01, (
        f"Excel rate mismatch: excel={excel['rate']}, expected={inputs['rate']}"
    )
    expected_months = int(inputs["tenure_years"]) * 12
    assert int(excel["tenure_months"]) == expected_months, (
        f"Excel tenure mismatch: excel={excel['tenure_months']}, "
        f"expected={expected_months}"
    )

    schedule_rows = excel["schedule_rows"]
    assert len(schedule_rows) == expected_months, (
        f"Excel schedule row count mismatch: excel={len(schedule_rows)}, "
        f"expected={expected_months}"
    )
    assert schedule_rows[-1]["balance"] == 0, (
        f"Final balance should be 0, got {schedule_rows[-1]['balance']}"
    )

    for row in schedule_rows:
        assert abs(row["total_payment"] - displayed["emi"]) <= tolerance, (
            f"Month {row['month']} EMI mismatch: excel={row['total_payment']}, "
            f"screen={displayed['emi']}"
        )
