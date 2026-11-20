"""Data-layer tests with mocks (network failures must degrade, never fabricate)."""
import pandas as pd
import pytest
from unittest import mock

from src import data_collection as dc


def _fake_download(rows=100):
    idx = pd.date_range("2025-01-01", periods=rows)
    px = pd.DataFrame({"Close": 100 + range(rows)}, index=idx)
    px.columns = pd.MultiIndex.from_product([["Close"], ["FAKE"]])
    return px


def test_quality_checks_flags_constant_column():
    df = pd.DataFrame({"A": range(50), "B": [1.0] * 50})
    qc = dc.quality_checks(df)
    assert not qc["pass"]
    assert any("constant" in i for i in qc["issues"])


def test_quality_checks_passes_clean_frame():
    idx = pd.date_range(end=pd.Timestamp.today().normalize(), periods=50, freq="h")
    df = pd.DataFrame({"A": range(50), "B": [x * 2 for x in range(50)]}, index=idx)
    assert dc.quality_checks(df)["pass"]


def test_fetch_prices_retries_then_raises():
    with mock.patch("yfinance.download", side_effect=Exception("network down")):
        with pytest.raises(RuntimeError, match="failed after"):
            dc.fetch_prices(["FAKE"], "2025-01-01", "2025-03-01", retries=1)


def test_fred_graceful_none_on_error():
    with mock.patch("requests.get", side_effect=Exception("offline")):
        assert dc.get_fred_series("DGS10") is None


def test_live_risk_free_rate_none_when_fred_down():
    with mock.patch("src.data_collection.get_fred_series", return_value=None):
        assert dc.live_risk_free_rate() == (None, None)
