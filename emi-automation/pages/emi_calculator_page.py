"""Page Object for emicalculator.net Home Loan calculator."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import expect

from config.settings import (
    AMOUNT_MAX,
    AMOUNT_MIN,
    RATE_MAX,
    RATE_MIN,
    TENURE_YEARS_MAX,
    TENURE_YEARS_MIN,
)
from pages.base_page import BasePage
from pages.driver_setup import DriverSetup
from utils.helpers import parse_currency

_TABLE_ROWS_SCRIPT = """() => {
  const table = document.querySelector('#emipaymentdetails table');
  if (!table) return [];
  return Array.from(table.rows)
    .map(row => {
      const yearCell = row.querySelector('.paymentyear');
      if (!yearCell || !yearCell.innerText.trim()) return null;
      const currencies = Array.from(row.querySelectorAll('.currency'))
        .map(cell => cell.innerText.trim());
      return {
        year: yearCell.innerText.trim(),
        principalText: currencies[0] || '',
        interestText: currencies[1] || '',
        totalPaymentText: currencies[2] || '',
        balanceText: currencies[3] || '',
      };
    })
    .filter(Boolean);
}"""

_BAR_CHART_SCRIPT = """() => {
  const bar = (window.Highcharts?.charts || [])
    .find(chart => chart?.renderTo?.id === 'emibarchart');
  if (!bar) throw new Error('Payment schedule bar chart not found');
  const categories = bar.xAxis[0].categories;
  const seriesData = name => {
    const series = bar.series.find(item => item.name === name);
    return series
      ? series.data.map(point => (typeof point === 'object' ? point.y : point))
      : [];
  };
  const principal = seriesData('Principal');
  const interest = seriesData('Interest');
  const balance = seriesData('Balance');
  return categories.map((year, index) => ({
    year: String(year),
    principal: principal[index] ?? 0,
    interest: interest[index] ?? 0,
    balance: balance[index] ?? 0,
  }));
}"""


class EmiCalculatorPage(BasePage):
    # Locators discovered via Selenium MCP accessibility snapshot
    HOME_LOAN_TAB = "#home-loan"
    LOAN_AMOUNT_INPUT = "#loanamount"
    LOAN_AMOUNT_SLIDER = "#loanamountslider"
    INTEREST_RATE_SLIDER = "#loaninterestslider"
    TENURE_SLIDER = "#loantermslider"
    TENURE_YEARS_RADIO = "#loanyears"
    LOAN_PRODUCT = "#loanproduct"
    EMI_AMOUNT = "#emiamount"
    TOTAL_INTEREST = "#emitotalinterest"
    TOTAL_PAYMENT = "#emitotalamount"
    PAYMENT_DETAILS = "#emipaymentdetails"
    YEAR_FORMAT_SELECT = "#yearformat"
    BAR_CHART = "#emibarchart"
    EXCEL_DOWNLOAD = "a.ecaldownloadexcel"

    def __init__(self, driver: DriverSetup) -> None:
        super().__init__(driver)

    def open(self) -> EmiCalculatorPage:
        self.navigate()
        self.wait_for_visible(self.LOAN_AMOUNT_INPUT)
        return self

    def ensure_home_loan_tab(self) -> None:
        self.click(self.HOME_LOAN_TAB)
        expect(self.driver.locator(self.LOAN_PRODUCT)).to_have_value("home-loan")

    def set_loan_amount_slider(self, amount: int) -> None:
        self.set_slider_by_value(
            self.driver.locator(self.LOAN_AMOUNT_SLIDER),
            amount,
            AMOUNT_MIN,
            AMOUNT_MAX,
        )

    def set_interest_rate_slider(self, rate: float) -> None:
        self.set_slider_by_value(
            self.driver.locator(self.INTEREST_RATE_SLIDER),
            rate,
            RATE_MIN,
            RATE_MAX,
        )

    def set_tenure_slider_years(self, years: int) -> None:
        self.driver.locator(self.TENURE_YEARS_RADIO).check()
        self.set_slider_by_value(
            self.driver.locator(self.TENURE_SLIDER),
            years,
            TENURE_YEARS_MIN,
            TENURE_YEARS_MAX,
        )

    def _read_currency_from_container(self, container_id: str) -> int:
        return parse_currency(self.get_text(container_id))

    def get_results(self) -> dict[str, int]:
        return {
            "emi": self._read_currency_from_container(self.EMI_AMOUNT),
            "total_interest": self._read_currency_from_container(self.TOTAL_INTEREST),
            "total_payment": self._read_currency_from_container(self.TOTAL_PAYMENT),
        }

    def assert_results_visible(self) -> None:
        self.wait_for_visible(self.EMI_AMOUNT)
        self.wait_for_visible(self.TOTAL_INTEREST)
        self.wait_for_visible(self.TOTAL_PAYMENT)

    def scroll_to_schedule(self) -> None:
        self.driver.locator(self.PAYMENT_DETAILS).scroll_into_view_if_needed()
        self.wait_for_visible(self.YEAR_FORMAT_SELECT)
        self.wait_for_visible(self.BAR_CHART)

    def select_year_format(self, value: str) -> None:
        self.driver.locator(self.YEAR_FORMAT_SELECT).select_option(value)
        self.wait_for_recalc(600)

    def _parse_schedule_rows(self, raw_rows: list[dict]) -> list[dict]:
        return [
            {
                "year": row["year"],
                "principal": parse_currency(row["principalText"]),
                "interest": parse_currency(row["interestText"]),
                "total_payment": parse_currency(row["totalPaymentText"]),
                "balance": parse_currency(row["balanceText"]),
            }
            for row in raw_rows
        ]

    def _parse_chart_rows(self, raw_rows: list[dict]) -> list[dict]:
        return [
            {
                "year": row["year"],
                "principal": round(row["principal"]),
                "interest": round(row["interest"]),
                "total_payment": round(row["principal"] + row["interest"]),
                "balance": round(row["balance"]),
            }
            for row in raw_rows
        ]

    def get_schedule_table_rows(self) -> list[dict]:
        raw_rows = self.page.evaluate(_TABLE_ROWS_SCRIPT)
        return self._parse_schedule_rows(raw_rows)

    def get_bar_chart_rows(self) -> list[dict]:
        raw_rows = self.page.evaluate(_BAR_CHART_SCRIPT)
        return self._parse_chart_rows(raw_rows)

    def download_excel(self, destination_dir: Path) -> Path:
        """Click Download Excel and save the file to destination_dir."""
        self.scroll_to_schedule()
        download_link = self.driver.locator(self.EXCEL_DOWNLOAD)
        download_link.scroll_into_view_if_needed()

        with self.page.expect_download() as download_info:
            download_link.click()

        download = download_info.value
        file_path = destination_dir / download.suggested_filename
        download.save_as(file_path)
        return file_path
