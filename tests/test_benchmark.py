import tempfile
from pathlib import Path

from diffradius.benchmark import all_cases, materialize, run_oracle, run_visible_tests


def test_benchmark_has_enough_cases_and_a_hard_case():
    cases = all_cases()
    assert len(cases) >= 10
    assert any(case.hard for case in cases)
    assert sum(1 for case in cases if not case.expected) >= 2


def test_every_expected_path_exists():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for spec in all_cases():
            case = materialize(spec.id, root)
            files = {p.relative_to(case.repo).as_posix() for p in case.repo.rglob("*") if p.is_file()}
            for risk in case.expected:
                assert set(risk.paths).intersection(files)


def test_visible_tests_pass_and_oracles_encode_ground_truth():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for spec in all_cases():
            before = materialize(spec.id, root, "before")
            after = materialize(spec.id, root, "after")
            assert run_visible_tests(before).returncode == 0, f"{spec.id}: before visible tests fail"
            assert run_visible_tests(after).returncode == 0, f"{spec.id}: after visible tests fail"
            before_oracle = run_oracle(before)
            after_oracle = run_oracle(after)
            assert before_oracle.returncode == 0, f"{spec.id}: oracle must pass before the change\n{before_oracle.stderr}"
            if after.expected:
                assert after_oracle.returncode != 0, f"{spec.id}: oracle should expose regression"
            else:
                assert after_oracle.returncode == 0, f"{spec.id}: safe control should pass oracle"
