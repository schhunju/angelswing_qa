"""Payment schedule chart vs table validation (TC-FN-09 / TC-SCHD-02–06)."""

import logging

import pytest

from utils.helpers import get_test_data
from validators.results import assert_schedule_matches_chart, assert_schedule_total_matches

logger = logging.getLogger(__name__)
YEAR_FORMATS = get_test_data("year_formats")


@pytest.mark.schedule
class TestPaymentSchedule:
    """Payment schedule: bar chart and table must agree year-wise for each view."""

    def _set_reference_inputs(self, app_page, case: dict) -> None:
        """Set TC-FN-09 reference loan values via sliders."""
        logger.info(
            "Setting principal=₹%s, rate=%s%%, tenure=%s years",
            f"{case['principal']:,}",
            case["rate"],
            case["tenure_years"],
        )
        app_page.set_loan_amount_slider(case["principal"])
        app_page.set_interest_rate_slider(case["rate"])
        app_page.set_tenure_slider_years(case["tenure_years"])

    @pytest.mark.parametrize(
        "year_format",
        YEAR_FORMATS,
        ids=[item["value"] for item in YEAR_FORMATS],
    )
    def test_chart_table_match_year_wise(self, app_page, year_format):
        """Calendar and financial year views: chart rows match table rows."""
        case = get_test_data("schedule_reference_case")
        logger.info("Test case %s — year format: %s", case["id"], year_format["label"])

        # Step 1: Set loan inputs and open the payment schedule section.
        self._set_reference_inputs(app_page, case)
        app_page.assert_results_visible()
        app_page.scroll_to_schedule()

        # Step 2: Switch between Calendar Year wise and Financial Year wise.
        logger.info("Selecting year format: %s", year_format["label"])
        app_page.select_year_format(year_format["value"])

        # Step 3: Read year-wise rows from the schedule table and bar chart.
        table_rows = app_page.get_schedule_table_rows()
        chart_rows = app_page.get_bar_chart_rows()
        logger.info("Comparing %s schedule rows with bar chart", len(table_rows))

        # Step 4: Validate principal, interest, balance, and total per year (±₹1).
        assert_schedule_matches_chart(table_rows, chart_rows)
        logger.info("Chart vs table match passed for all years")

        # Step 5: Sum of schedule rows must match headline Total Payment.
        headline = app_page.get_results()
        schedule_total = sum(row["total_payment"] for row in table_rows)
        logger.info(
            "Schedule total: ₹%s | Headline total: ₹%s",
            f"{schedule_total:,}",
            f"{headline['total_payment']:,}",
        )
        assert_schedule_total_matches(table_rows, headline["total_payment"])
        logger.info("Schedule total validation passed")
