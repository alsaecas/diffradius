from benchmarks.schema import Case, RiskSpec

CASES = (
    Case(
        id='13-safe-refactor',
        title='Safe internal refactor negative control',
        ticket='Extract display-name formatting into a helper without changing behavior.',
        before={'app/names.py': 'def label(first, last):\n    return (first.strip() + " " + last.strip()).strip()\n', 'tests/test_visible.py': 'from app.names import label\n\ndef test_label(): assert label(" Ada ", " Lovelace ") == "Ada Lovelace"\n', 'app/__init__.py': ''},
        after={'app/names.py': 'def _clean(value):\n    return value.strip()\n\ndef label(first, last):\n    return (_clean(first) + " " + _clean(last)).strip()\n', 'tests/test_visible.py': 'from app.names import label\n\ndef test_label(): assert label(" Ada ", " Lovelace ") == "Ada Lovelace"\n', 'app/__init__.py': ''},
        oracle='from app.names import label\nassert label("", " Solo ") == "Solo"\nassert label(" Ada ", "") == "Ada"\n',
        expected=(),
        hard=False,
    ),
    Case(
        id='14-safe-config',
        title='Safe configuration normalization negative control',
        ticket='Normalize explicit issuer values to a tuple while preserving missing-value semantics.',
        before={'app/config.py': 'def issuers(raw):\n    return raw.get("additional_issuers")\n', 'tests/test_visible.py': 'from app.config import issuers\n\ndef test_missing(): assert issuers({}) is None\n', 'app/__init__.py': ''},
        after={'app/config.py': 'def issuers(raw):\n    value = raw.get("additional_issuers")\n    return tuple(value) if value is not None else None\n', 'tests/test_visible.py': 'from app.config import issuers\n\ndef test_missing(): assert issuers({}) is None\n', 'app/__init__.py': ''},
        oracle='from app.config import issuers\nassert issuers({}) is None\nassert issuers({"additional_issuers": ["a"]}) == ("a",)\n',
        expected=(),
        hard=False,
    ),
)
