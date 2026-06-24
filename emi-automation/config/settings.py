"""Load base URL from config/appconfig.ini; other settings live here."""

from __future__ import annotations

import os
from configparser import ConfigParser
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "appconfig.ini"

_config = ConfigParser()
if not _config.read(CONFIG_PATH):
    raise FileNotFoundError(f"Application config not found: {CONFIG_PATH}")

_active_env = os.getenv("TEST_ENV", _config.get("env", "active")).strip()
if _active_env not in _config:
    raise ValueError(
        f"Unknown environment '{_active_env}'. "
        f"Available: {[s for s in _config.sections() if s != 'env']}"
    )

BASE_URL = _config.get(_active_env, "base_url").strip()

EMI_TOLERANCE = 1
DEFAULT_TIMEOUT_MS = 10000
RECALC_WAIT_MS = 400

# Home Loan slider ranges (from test plan)
AMOUNT_MIN = 0
AMOUNT_MAX = 200_00_000
RATE_MIN = 5.0
RATE_MAX = 20.0
TENURE_YEARS_MIN = 0
TENURE_YEARS_MAX = 30
