"""Excel export validation (TC-FN-10 / TC-EXP-02)."""

import logging

import pytest

from utils.helpers import get_test_data, parse_excel_export
from validators.results import assert_excel_matches_screen

logger = logging.getLogger(__name__)


@pytest.mark.export
class TestExcelExport:
    """Download Excel and verify exported values match on-screen calculator results."""

    def test_excel_values_match_on_screen(self, app_page, tmp_path):
        """TC-FN-10: Excel summary and schedule match displayed EMI results."""
        case = get_test_data("slider_test_case")
        logger.info(
            "Test case %s: principal=₹%s, rate=%s%%, tenure=%s years",
            case["id"],
            f"{case['principal']:,}",
            case["rate"],
            case["tenure_years"],
        )

        # Step 1: Set loan inputs via sliders.
        logger.info("Setting loan amount slider to ₹%s", f"{case['principal']:,}")
        app_page.set_loan_amount_slider(case["principal"])
        logger.info("Setting interest rate slider to %s%%", case["rate"])
        app_page.set_interest_rate_slider(case["rate"])
        logger.info("Setting tenure slider to %s years", case["tenure_years"])
        app_page.set_tenure_slider_years(case["tenure_years"])

        # Step 2: Read on-screen EMI summary before export.
        app_page.assert_results_visible()
        displayed = app_page.get_results()
        logger.info(
            "On-screen results — EMI: ₹%s, Interest: ₹%s, Total: ₹%s",
            f"{displayed['emi']:,}",
            f"{displayed['total_interest']:,}",
            f"{displayed['total_payment']:,}",
        )

        # Step 3: Download Excel and parse exported values.
        excel_path = app_page.download_excel(tmp_path)
        assert excel_path.suffix == ".xlsx", f"Unexpected download type: {excel_path.name}"
        assert excel_path.stat().st_size > 0, "Downloaded Excel file is empty"
        logger.info("Downloaded Excel: %s (%s bytes)", excel_path.name, excel_path.stat().st_size)

        excel_data = parse_excel_export(excel_path)
        logger.info(
            "Excel summary — EMI: ₹%s, Interest: ₹%s, Total: ₹%s, rows: %s",
            f"{excel_data['emi']:,}",
            f"{excel_data['total_interest']:,}",
            f"{excel_data['total_payment']:,}",
            len(excel_data["schedule_rows"]),
        )

        # Step 4: Compare Excel values with on-screen results and inputs.
        assert_excel_matches_screen(excel_data, displayed, case)
        logger.info("Excel export validation passed")
