"""Headless smoke tests: every page of the Streamlit app executes end-to-end
(with live data fetches) using streamlit.testing.v1.AppTest."""
import pathlib
import pytest

from streamlit.testing.v1 import AppTest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGES = ["app.py"] + sorted(str(p.relative_to(ROOT)) for p in (ROOT / "pages").glob("*.py"))


@pytest.mark.parametrize("page", PAGES)
def test_page_runs(page):
    at = AppTest.from_file(str(ROOT / page), default_timeout=300)
    at.run()
    assert not at.exception, f"{page} raised: {at.exception}"
