from benchmarks.schema import Case, RiskSpec

CASES = (
    Case(
        id='01-error-propagation',
        title='Changed exception contract breaks an unguarded caller',
        ticket='Stop swallowing OrganizationLookupError in load_roles so callers can surface failures.',
        before={'app/service.py': 'class OrganizationLookupError(RuntimeError):\n    pass\n\n\ndef load_roles(client, org_id):\n    try:\n        return client.fetch_roles(org_id)\n    except OrganizationLookupError:\n        return []\n', 'app/form.py': 'from app.service import load_roles\n\n\nclass Form:\n    def __init__(self, client):\n        self.client = client\n        self.roles = []\n\n    def switch_org(self, org_id):\n        self.roles = load_roles(self.client, org_id)\n        return "ready"\n', 'tests/test_visible.py': 'from app.service import load_roles\n\n\nclass Client:\n    def fetch_roles(self, org_id):\n        return ["admin"]\n\n\ndef test_happy_path():\n    assert load_roles(Client(), "acme") == ["admin"]\n', 'app/__init__.py': ''},
        after={'app/service.py': 'class OrganizationLookupError(RuntimeError):\n    pass\n\n\ndef load_roles(client, org_id):\n    return client.fetch_roles(org_id)\n', 'app/form.py': 'from app.service import load_roles\n\n\nclass Form:\n    def __init__(self, client):\n        self.client = client\n        self.roles = []\n\n    def switch_org(self, org_id):\n        self.roles = load_roles(self.client, org_id)\n        return "ready"\n', 'tests/test_visible.py': 'from app.service import load_roles\n\n\nclass Client:\n    def fetch_roles(self, org_id):\n        return ["admin"]\n\n\ndef test_happy_path():\n    assert load_roles(Client(), "acme") == ["admin"]\n', 'app/__init__.py': ''},
        oracle='from app.form import Form\nfrom app.service import OrganizationLookupError\n\nclass BrokenClient:\n    def fetch_roles(self, org_id):\n        raise OrganizationLookupError("down")\n\nform = Form(BrokenClient())\nassert form.switch_org("x") == "ready"\nassert form.roles == []\n',
        expected=(RiskSpec('error_propagation', ('app/form.py',)),),
        hard=False,
    ),
    Case(
        id='02-stale-state',
        title='Error handling preserves stale state',
        ticket='Handle role-loading failures inside the form so the UI remains usable.',
        before={'app/form.py': 'class Form:\n    def __init__(self, client):\n        self.client = client\n        self.roles = []\n\n    def switch_org(self, org_id):\n        try:\n            self.roles = self.client.fetch_roles(org_id)\n        except RuntimeError:\n            self.roles = []\n        return self.roles\n', 'tests/test_visible.py': 'from app.form import Form\n\nclass Client:\n    def fetch_roles(self, org_id):\n        return [org_id]\n\ndef test_success():\n    assert Form(Client()).switch_org("a") == ["a"]\n', 'app/__init__.py': ''},
        after={'app/form.py': 'class Form:\n    def __init__(self, client):\n        self.client = client\n        self.roles = []\n\n    def switch_org(self, org_id):\n        try:\n            self.roles = self.client.fetch_roles(org_id)\n        except RuntimeError:\n            pass\n        return self.roles\n', 'tests/test_visible.py': 'from app.form import Form\n\nclass Client:\n    def fetch_roles(self, org_id):\n        return [org_id]\n\ndef test_success():\n    assert Form(Client()).switch_org("a") == ["a"]\n', 'app/__init__.py': ''},
        oracle='from app.form import Form\n\nclass Client:\n    def __init__(self): self.n = 0\n    def fetch_roles(self, org_id):\n        self.n += 1\n        if self.n == 2: raise RuntimeError("down")\n        return [org_id]\n\nform = Form(Client())\nassert form.switch_org("old") == ["old"]\nassert form.switch_org("new") == []\n',
        expected=(RiskSpec('stale_state', ('app/form.py',)),),
        hard=False,
    ),
    Case(
        id='03-data-compatibility',
        title='New required field breaks existing records',
        ticket='Expose region in account summaries.',
        before={'app/accounts.py': 'def summarize(row):\n    return {"id": row["id"], "name": row["name"]}\n', 'tests/test_visible.py': 'from app.accounts import summarize\n\ndef test_new_record():\n    assert summarize({"id": 1, "name": "Ada", "region": "eu"})["name"] == "Ada"\n', 'app/__init__.py': ''},
        after={'app/accounts.py': 'def summarize(row):\n    return {"id": row["id"], "name": row["name"], "region": row["region"]}\n', 'tests/test_visible.py': 'from app.accounts import summarize\n\ndef test_new_record():\n    assert summarize({"id": 1, "name": "Ada", "region": "eu"})["region"] == "eu"\n', 'app/__init__.py': ''},
        oracle='from app.accounts import summarize\nassert summarize({"id": 7, "name": "Legacy"}) == {"id": 7, "name": "Legacy", "region": None}\n',
        expected=(RiskSpec('data_compatibility', ('app/accounts.py',)),),
        hard=False,
    ),
    Case(
        id='04-interface-contract',
        title='Response rename breaks an internal consumer',
        ticket='Rename API response field company to organization for consistency.',
        before={'app/api.py': 'def response(account):\n    return {"id": account["id"], "company": account["company"]}\n', 'app/export.py': 'from app.api import response\n\ndef csv_row(account):\n    payload = response(account)\n    return f"{payload[\'id\']},{payload[\'company\']}"\n', 'tests/test_visible.py': 'from app.api import response\n\ndef test_new_api_shape_baseline():\n    assert response({"id": 1, "company": "A"})["id"] == 1\n', 'app/__init__.py': ''},
        after={'app/api.py': 'def response(account):\n    return {"id": account["id"], "organization": account["company"]}\n', 'app/export.py': 'from app.api import response\n\ndef csv_row(account):\n    payload = response(account)\n    return f"{payload[\'id\']},{payload[\'company\']}"\n', 'tests/test_visible.py': 'from app.api import response\n\ndef test_new_api_shape():\n    assert response({"id": 1, "company": "A"})["organization"] == "A"\n', 'app/__init__.py': ''},
        oracle='from app.export import csv_row\nassert csv_row({"id": 1, "company": "Acme"}) == "1,Acme"\n',
        expected=(RiskSpec('interface_contract', ('app/export.py',)),),
        hard=False,
    ),
)
