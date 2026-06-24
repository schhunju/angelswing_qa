"""Home Loan slider E2E test — update inputs via sliders and validate EMI via formula."""

import logging

import pytest

from utils.helpers import calculate_totals, get_test_data
from validators.results import assert_emi_matches_formula

logger = logging.getLogger(__name__)


@pytest.mark.smoke
class TestHomeLoanSlider:
    """Home Loan slider flow: set inputs via UI sliders and validate EMI using formula."""

    def test_slider_updates_and_emi_matches_formula(self, app_page):
        """TC-SMK-01: sliders update amount, rate, tenure; EMI matches formula."""
        case = get_test_data("slider_test_case")
        principal = case["principal"]
        rate = case["rate"]
        years = case["tenure_years"]
        tenure_months = years * 12

        logger.info(
            "Test case %s: principal=₹%s, rate=%s%%, tenure=%s years",
            case["id"],
            f"{principal:,}",
            rate,
            years,
        )

        # Step 1: Set all three inputs using sliders only (no typing into fields).
        logger.info("Setting loan amount slider to ₹%s", f"{principal:,}")
        app_page.set_loan_amount_slider(principal)
        logger.info("Setting interest rate slider to %s%%", rate)
        app_page.set_interest_rate_slider(rate)
        logger.info("Setting tenure slider to %s years", years)
        app_page.set_tenure_slider_years(years)

        # Step 2: Read EMI, total interest, and total payment from the results panel.
        app_page.assert_results_visible()
        displayed = app_page.get_results()
        expected = calculate_totals(principal, rate, tenure_months)

        logger.info(
            "UI results — EMI: ₹%s, Interest: ₹%s, Total: ₹%s",
            f"{displayed['emi']:,}",
            f"{displayed['total_interest']:,}",
            f"{displayed['total_payment']:,}",
        )
        logger.info(
            "Formula expected — EMI: ₹%s, Interest: ₹%s, Total: ₹%s",
            f"{expected['emi']:,}",
            f"{expected['total_interest']:,}",
            f"{expected['total_payment']:,}",
        )

        # Step 3: Compare displayed values with formula-based expectations (±₹1).
        assert_emi_matches_formula(displayed, expected, principal, tenure_months)
        logger.info("EMI validation passed")
