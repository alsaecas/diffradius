from benchmarks.schema import Case, RiskSpec

CASES = (
    Case(
        id='09-async-lifecycle',
        title='Background task error no longer reaches caller',
        ticket='Make notification sending non-blocking.',
        before={'app/notify.py': 'import asyncio\n\nasync def submit(sender, message):\n    await sender.send(message)\n    return "sent"\n', 'tests/test_visible.py': 'import asyncio\nfrom app.notify import submit\n\nclass Sender:\n    async def send(self, message): return None\n\ndef test_success():\n    assert asyncio.run(submit(Sender(), "x")) == "sent"\n', 'app/__init__.py': ''},
        after={'app/notify.py': 'import asyncio\n\nasync def submit(sender, message):\n    asyncio.create_task(sender.send(message))\n    return "sent"\n', 'tests/test_visible.py': 'import asyncio\nfrom app.notify import submit\n\nclass Sender:\n    async def send(self, message): return None\n\ndef test_success():\n    assert asyncio.run(submit(Sender(), "x")) == "sent"\n', 'app/__init__.py': ''},
        oracle='import asyncio\nfrom app.notify import submit\nclass Sender:\n    def __init__(self): self.sent = False\n    async def send(self, message):\n        await asyncio.sleep(0.01)\n        self.sent = True\nasync def run():\n    sender = Sender()\n    await submit(sender, "x")\n    assert sender.sent is True\nasyncio.run(run())\n',
        expected=(RiskSpec('async_lifecycle', ('app/notify.py',)),),
        hard=False,
    ),
    Case(
        id='10-security-validation',
        title='Archive extraction accepts path traversal',
        ticket='Support nested paths while importing archive entries.',
        before={'app/archive.py': 'from pathlib import Path\n\ndef target(root, name):\n    root = Path(root).resolve()\n    candidate = (root / name).resolve()\n    candidate.relative_to(root)\n    return candidate\n', 'tests/test_visible.py': 'from app.archive import target\n\ndef test_nested(tmp_path):\n    assert target(tmp_path, "a/b.txt").name == "b.txt"\n', 'app/__init__.py': ''},
        after={'app/archive.py': 'from pathlib import Path\n\ndef target(root, name):\n    return (Path(root) / name).resolve()\n', 'tests/test_visible.py': 'from app.archive import target\n\ndef test_nested(tmp_path):\n    assert target(tmp_path, "a/b.txt").name == "b.txt"\n', 'app/__init__.py': ''},
        oracle='from pathlib import Path\nfrom tempfile import TemporaryDirectory\nfrom app.archive import target\nwith TemporaryDirectory() as d:\n    root = Path(d) / "root"; root.mkdir()\n    try: target(root, "../escape.txt")\n    except ValueError: pass\n    else: raise AssertionError("path traversal accepted")\n',
        expected=(RiskSpec('security_validation', ('app/archive.py',)),),
        hard=False,
    ),
    Case(
        id='11-cache-consistency',
        title='Mutation stops invalidating cached reads',
        ticket='Simplify profile updates by removing redundant cache operations.',
        before={'app/profile.py': 'def get_profile(db, cache, user_id):\n    if user_id not in cache: cache[user_id] = db[user_id]\n    return cache[user_id]\n\ndef update_profile(db, cache, user_id, value):\n    db[user_id] = value\n    cache.pop(user_id, None)\n', 'tests/test_visible.py': 'from app.profile import update_profile\n\ndef test_update_db():\n    db={1:"old"}; cache={}\n    update_profile(db, cache, 1, "new")\n    assert db[1] == "new"\n', 'app/__init__.py': ''},
        after={'app/profile.py': 'def get_profile(db, cache, user_id):\n    if user_id not in cache: cache[user_id] = db[user_id]\n    return cache[user_id]\n\ndef update_profile(db, cache, user_id, value):\n    db[user_id] = value\n', 'tests/test_visible.py': 'from app.profile import update_profile\n\ndef test_update_db():\n    db={1:"old"}; cache={}\n    update_profile(db, cache, 1, "new")\n    assert db[1] == "new"\n', 'app/__init__.py': ''},
        oracle='from app.profile import get_profile, update_profile\ndb={1:"old"}; cache={}\nassert get_profile(db, cache, 1) == "old"\nupdate_profile(db, cache, 1, "new")\nassert get_profile(db, cache, 1) == "new"\n',
        expected=(RiskSpec('cache_consistency', ('app/profile.py',)),),
        hard=False,
    ),
    Case(
        id='12-indirect-dependency',
        title='Indirect caller assumes old error behavior',
        ticket='Allow repository lookup failures to propagate so API callers can choose their response.',
        before={'app/repository.py': 'def find(repo, key):\n    try: return repo[key]\n    except KeyError: return None\n', 'app/service.py': 'from app.repository import find\n\ndef display_name(repo, key):\n    item = find(repo, key)\n    return item["name"] if item else "unknown"\n', 'app/scheduler.py': 'from app.service import display_name\n\ndef build_label(repo, key):\n    return "user:" + display_name(repo, key)\n', 'tests/test_visible.py': 'from app.scheduler import build_label\n\ndef test_found():\n    assert build_label({1:{"name":"Ada"}}, 1) == "user:Ada"\n', 'app/__init__.py': ''},
        after={'app/repository.py': 'def find(repo, key):\n    return repo[key]\n', 'app/service.py': 'from app.repository import find\n\ndef display_name(repo, key):\n    item = find(repo, key)\n    return item["name"] if item else "unknown"\n', 'app/scheduler.py': 'from app.service import display_name\n\ndef build_label(repo, key):\n    return "user:" + display_name(repo, key)\n', 'tests/test_visible.py': 'from app.scheduler import build_label\n\ndef test_found():\n    assert build_label({1:{"name":"Ada"}}, 1) == "user:Ada"\n', 'app/__init__.py': ''},
        oracle='from app.scheduler import build_label\nassert build_label({}, 42) == "user:unknown"\n',
        expected=(RiskSpec('indirect_dependency', ('app/service.py', 'app/scheduler.py')),),
        hard=True,
    ),
)
