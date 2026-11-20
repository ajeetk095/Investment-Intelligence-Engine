"""Security-oriented tests: no secrets in tree, safe config, input handling."""
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]

SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key\s*=\s*['\"][A-Za-z0-9]{16,})", re.I),
    re.compile(r"(secret\s*=\s*['\"][A-Za-z0-9]{16,})", re.I),
    re.compile(r"(password\s*=\s*['\"]\S{6,})", re.I),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]


SCAN_DIRS = ["src", "pages", "config", "app.py"]


def _py_targets():
    for d in SCAN_DIRS[:-1]:
        yield from (ROOT / d).rglob("*.py")
    yield ROOT / "app.py"


def test_no_hardcoded_secrets():
    offenders = []
    for path in _py_targets():
        text = path.read_text(errors="ignore")
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                offenders.append(str(path))
    assert not offenders, f"hardcoded secrets in: {offenders}"


def test_env_example_has_no_real_key():
    text = (ROOT / ".env.example").read_text()
    assert "your_free_fred_key_here" in text
    assert not re.search(r"=[A-Za-z0-9]{20,}", text)


def test_streamlit_xrsf_enabled():
    text = (ROOT / ".streamlit" / "config.toml").read_text()
    assert "enableXsrfProtection = true" in text


def test_no_eval_or_pickle():
    for path in _py_targets():
        text = path.read_text(errors="ignore")
        assert not re.search(r"\beval\s*\(", text), f"eval use in {path}"
        assert "pickle.load" not in text, f"pickle.load in {path}"


def test_gitignore_covers_env():
    text = (ROOT / ".gitignore").read_text()
    assert ".env" in text
