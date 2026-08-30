from benchmarks.schema import Case, RiskSpec

CASES = (
    Case(
        id='05-authorization',
        title='Authorization check moved after side effect',
        ticket='Simplify the admin delete endpoint by centralizing permission handling.',
        before={'app/admin.py': 'def delete_user(actor, store, user_id):\n    if not actor.get("admin"):\n        return False\n    store.pop(user_id, None)\n    return True\n', 'tests/test_visible.py': 'from app.admin import delete_user\n\ndef test_admin_delete():\n    store = {1: "x"}\n    assert delete_user({"admin": True}, store, 1)\n    assert store == {}\n', 'app/__init__.py': ''},
        after={'app/admin.py': 'def delete_user(actor, store, user_id):\n    store.pop(user_id, None)\n    if not actor.get("admin"):\n        return False\n    return True\n', 'tests/test_visible.py': 'from app.admin import delete_user\n\ndef test_admin_delete():\n    store = {1: "x"}\n    assert delete_user({"admin": True}, store, 1)\n    assert store == {}\n', 'app/__init__.py': ''},
        oracle='from app.admin import delete_user\nstore = {1: "x"}\nassert delete_user({"admin": False}, store, 1) is False\nassert store == {1: "x"}\n',
        expected=(RiskSpec('authorization', ('app/admin.py',)),),
        hard=False,
    ),
    Case(
        id='06-configuration',
        title='Default configuration changes enabled behavior',
        ticket='Make the optional issuer list easier to consume by returning an empty list by default.',
        before={'app/config.py': 'def issuers(raw):\n    return raw.get("additional_issuers")\n\ndef should_enable_external_auth(raw):\n    return issuers(raw) is not None\n', 'tests/test_visible.py': 'from app.config import issuers\n\ndef test_explicit_issuers():\n    assert issuers({"additional_issuers": ["a"]}) == ["a"]\n', 'app/__init__.py': ''},
        after={'app/config.py': 'def issuers(raw):\n    return raw.get("additional_issuers", [])\n\ndef should_enable_external_auth(raw):\n    return issuers(raw) is not None\n', 'tests/test_visible.py': 'from app.config import issuers\n\ndef test_explicit_issuers():\n    assert issuers({"additional_issuers": ["a"]}) == ["a"]\n', 'app/__init__.py': ''},
        oracle='from app.config import should_enable_external_auth\nassert should_enable_external_auth({}) is False\n',
        expected=(RiskSpec('configuration', ('app/config.py',), ('authorization', 'interface_contract')),),
        hard=False,
    ),
    Case(
        id='07-transactionality',
        title='Audit side effect escapes transaction rollback',
        ticket='Record an audit event when an account update starts.',
        before={'app/store.py': 'def update_account(db, account_id, value):\n    old = db["accounts"].get(account_id)\n    try:\n        db["accounts"][account_id] = value\n        if value == "bad": raise RuntimeError("validation")\n        db["audit"].append((account_id, value))\n    except Exception:\n        if old is None: db["accounts"].pop(account_id, None)\n        else: db["accounts"][account_id] = old\n        raise\n', 'tests/test_visible.py': 'from app.store import update_account\n\ndef test_success():\n    db = {"accounts": {}, "audit": []}\n    update_account(db, 1, "ok")\n    assert db["audit"] == [(1, "ok")]\n', 'app/__init__.py': ''},
        after={'app/store.py': 'def update_account(db, account_id, value):\n    old = db["accounts"].get(account_id)\n    db["audit"].append((account_id, value))\n    try:\n        db["accounts"][account_id] = value\n        if value == "bad": raise RuntimeError("validation")\n    except Exception:\n        if old is None: db["accounts"].pop(account_id, None)\n        else: db["accounts"][account_id] = old\n        raise\n', 'tests/test_visible.py': 'from app.store import update_account\n\ndef test_success():\n    db = {"accounts": {}, "audit": []}\n    update_account(db, 1, "ok")\n    assert db["audit"] == [(1, "ok")]\n', 'app/__init__.py': ''},
        oracle='from app.store import update_account\ndb = {"accounts": {}, "audit": []}\ntry: update_account(db, 1, "bad")\nexcept RuntimeError: pass\nassert db == {"accounts": {}, "audit": []}\n',
        expected=(RiskSpec('transactionality', ('app/store.py',)),),
        hard=False,
    ),
    Case(
        id='08-idempotency',
        title='Retry wrapper duplicates a side effect',
        ticket='Retry transient payment failures once.',
        before={'app/payments.py': 'def charge_once(gateway, account, amount):\n    return gateway.charge(account, amount)\n', 'tests/test_visible.py': 'from app.payments import charge_once\n\nclass Gateway:\n    def charge(self, account, amount): return "ok"\n\ndef test_success():\n    assert charge_once(Gateway(), "a", 10) == "ok"\n', 'app/__init__.py': ''},
        after={'app/payments.py': 'def charge_once(gateway, account, amount):\n    try:\n        return gateway.charge(account, amount)\n    except TimeoutError:\n        return gateway.charge(account, amount)\n', 'tests/test_visible.py': 'from app.payments import charge_once\n\nclass Gateway:\n    def charge(self, account, amount): return "ok"\n\ndef test_success():\n    assert charge_once(Gateway(), "a", 10) == "ok"\n', 'app/__init__.py': ''},
        oracle='from app.payments import charge_once\nclass Gateway:\n    def __init__(self): self.charges = 0\n    def charge(self, account, amount):\n        self.charges += 1\n        if self.charges == 1: raise TimeoutError("response lost after commit")\n        return "ok"\ng = Gateway()\ntry: charge_once(g, "a", 10)\nexcept TimeoutError: pass\nassert g.charges == 1\n',
        expected=(RiskSpec('idempotency', ('app/payments.py',)),),
        hard=False,
    ),
)
