from benchmarks.schema import Case, RiskSpec


CASES = (
    Case(
        id="15-multi-risk-access-cache",
        title="Permission cache introduces stale authorization and fail-open behavior",
        ticket="Cache directory scopes during permission checks to reduce repeated network calls.",
        before={
            "app/access.py": '''def can_write(directory, cache, user_id):\n    try:\n        scopes = directory.scopes(user_id)\n    except TimeoutError:\n        return False\n    return "write" in scopes\n''',
            "app/admin.py": '''def replace_scopes(directory, user_id, scopes):\n    directory.set_scopes(user_id, list(scopes))\n''',
            "app/__init__.py": "",
            "tests/test_visible.py": '''from app.access import can_write\n\nclass Directory:\n    def scopes(self, user_id): return ["write"]\n\ndef test_happy_path():\n    assert can_write(Directory(), {}, "u1") is True\n''',
        },
        after={
            "app/access.py": '''def can_write(directory, cache, user_id):\n    if user_id in cache:\n        return "write" in cache[user_id]\n    try:\n        scopes = directory.scopes(user_id)\n    except TimeoutError:\n        return True\n    cache[user_id] = list(scopes)\n    return "write" in scopes\n''',
            "app/admin.py": '''def replace_scopes(directory, user_id, scopes):\n    directory.set_scopes(user_id, list(scopes))\n''',
            "app/__init__.py": "",
            "tests/test_visible.py": '''from app.access import can_write\n\nclass Directory:\n    def scopes(self, user_id): return ["write"]\n\ndef test_happy_path():\n    cache = {}\n    assert can_write(Directory(), cache, "u1") is True\n    assert cache["u1"] == ["write"]\n''',
        },
        oracle='''from app.access import can_write\nfrom app.admin import replace_scopes\n\nclass Directory:\n    def __init__(self): self.values = {"u1": ["write"]}; self.fail = False\n    def scopes(self, user_id):\n        if self.fail: raise TimeoutError("directory unavailable")\n        return self.values[user_id]\n    def set_scopes(self, user_id, scopes): self.values[user_id] = scopes\n\ndirectory = Directory(); cache = {}\nassert can_write(directory, cache, "u1") is True\nreplace_scopes(directory, "u1", [])\nassert can_write(directory, cache, "u1") is False\ndirectory.fail = True\nassert can_write(directory, {}, "u1") is False\n''',
        expected=(
            RiskSpec("cache_consistency", ("app/access.py", "app/admin.py")),
            RiskSpec("authorization", ("app/access.py",)),
        ),
        hard=True,
    ),
    Case(
        id="16-identifier-normalization",
        title="Identifier normalization silently merges distinct existing identities",
        ticket="Normalize newly created external account IDs to lowercase for consistent lookups.",
        before={
            "app/accounts.py": '''def create(store, external_id, name):\n    if external_id in store:\n        raise ValueError("duplicate")\n    store[external_id] = name\n    return external_id\n''',
            "app/importer.py": '''from app.accounts import create\n\ndef import_rows(store, rows):\n    return [create(store, row["external_id"], row["name"]) for row in rows]\n''',
            "app/__init__.py": "",
            "tests/test_visible.py": '''from app.accounts import create\n\ndef test_create():\n    store = {}\n    assert create(store, "User-A", "Ada") == "User-A"\n''',
        },
        after={
            "app/accounts.py": '''def create(store, external_id, name):\n    if external_id in store:\n        raise ValueError("duplicate")\n    external_id = external_id.lower()\n    store[external_id] = name\n    return external_id\n''',
            "app/importer.py": '''from app.accounts import create\n\ndef import_rows(store, rows):\n    return [create(store, row["external_id"], row["name"]) for row in rows]\n''',
            "app/__init__.py": "",
            "tests/test_visible.py": '''from app.accounts import create\n\ndef test_create_is_normalized():\n    store = {}\n    assert create(store, "User-A", "Ada") == "user-a"\n''',
        },
        oracle='''from app.importer import import_rows\nstore = {"User-A": "Legacy uppercase", "user-a": "Legacy lowercase"}\nimport_rows(store, [{"external_id": "USER-A", "name": "New"}])\n# Normalizing a new identifier must not overwrite a distinct pre-existing identity.\nassert store["user-a"] == "Legacy lowercase"\nassert store["User-A"] == "Legacy uppercase"\n''',
        expected=(RiskSpec("data_compatibility", ("app/accounts.py", "app/importer.py")),),
        hard=True,
    ),
    Case(
        id="17-safe-timeout-refactor",
        title="Safe shared timeout constant negative control",
        ticket="Move the repeated five-second HTTP timeout into a shared constant without changing behavior.",
        before={
            "app/client.py": '''def fetch(http, url):\n    return http.get(url, timeout=5)\n''',
            "app/health.py": '''def ping(http, url):\n    return http.get(url, timeout=5).status == 200\n''',
            "app/__init__.py": "",
            "tests/test_visible.py": '''from app.client import fetch\n\nclass Http:\n    def get(self, url, timeout): return timeout\n\ndef test_timeout(): assert fetch(Http(), "x") == 5\n''',
        },
        after={
            "app/config.py": '''DEFAULT_HTTP_TIMEOUT = 5\n''',
            "app/client.py": '''from app.config import DEFAULT_HTTP_TIMEOUT\n\ndef fetch(http, url):\n    return http.get(url, timeout=DEFAULT_HTTP_TIMEOUT)\n''',
            "app/health.py": '''from app.config import DEFAULT_HTTP_TIMEOUT\n\ndef ping(http, url):\n    return http.get(url, timeout=DEFAULT_HTTP_TIMEOUT).status == 200\n''',
            "app/__init__.py": "",
            "tests/test_visible.py": '''from app.client import fetch\n\nclass Http:\n    def get(self, url, timeout): return timeout\n\ndef test_timeout(): assert fetch(Http(), "x") == 5\n''',
        },
        oracle='''from app.client import fetch\nfrom app.health import ping\nclass Response:\n    status = 200\nclass Http:\n    def __init__(self): self.timeouts = []\n    def get(self, url, timeout):\n        self.timeouts.append(timeout)\n        return Response() if url == "health" else timeout\nh = Http()\nassert fetch(h, "api") == 5\nassert ping(h, "health") is True\nassert h.timeouts == [5, 5]\n''',
        expected=(),
    ),
    Case(
        id="18-lazy-transaction-boundary",
        title="Lazy iterator escapes the transaction that owns its data",
        ticket="Reduce memory use by streaming repository rows instead of materializing the whole result.",
        before={
            "app/repository.py": '''def rows(db):\n    return list(db.read_rows())\n''',
            "app/export.py": '''from app.repository import rows\n\ndef export_names(db):\n    with db.transaction():\n        result = rows(db)\n    return [row["name"] for row in result]\n''',
            "app/__init__.py": "",
            "tests/test_visible.py": '''from app.repository import rows\n\nclass Db:\n    def read_rows(self): return iter([{"name": "Ada"}])\n\ndef test_rows(): assert list(rows(Db())) == [{"name": "Ada"}]\n''',
        },
        after={
            "app/repository.py": '''def rows(db):\n    return (row for row in db.read_rows())\n''',
            "app/export.py": '''from app.repository import rows\n\ndef export_names(db):\n    with db.transaction():\n        result = rows(db)\n    return [row["name"] for row in result]\n''',
            "app/__init__.py": "",
            "tests/test_visible.py": '''from app.repository import rows\n\nclass Db:\n    def read_rows(self): return iter([{"name": "Ada"}])\n\ndef test_rows(): assert list(rows(Db())) == [{"name": "Ada"}]\n''',
        },
        oracle='''from contextlib import contextmanager\nfrom app.export import export_names\n\nclass Db:\n    def __init__(self): self.active = False\n    @contextmanager\n    def transaction(self):\n        self.active = True\n        try: yield\n        finally: self.active = False\n    def read_rows(self):\n        def generate():\n            if not self.active: raise RuntimeError("cursor used after transaction")\n            yield {"name": "Ada"}\n        return generate()\n\nassert export_names(Db()) == ["Ada"]\n''',
        expected=(RiskSpec("indirect_dependency", ("app/export.py", "app/repository.py")),),
        hard=True,
    ),
)
