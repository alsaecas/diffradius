from benchmarks.cases_1 import CASES as CASES_1
from benchmarks.cases_2 import CASES as CASES_2
from benchmarks.cases_3 import CASES as CASES_3
from benchmarks.cases_4 import CASES as CASES_4
from benchmarks.cases_5 import CASES as CASES_5
from benchmarks.schema import Case, RiskSpec

CASES: tuple[Case, ...] = CASES_1 + CASES_2 + CASES_3 + CASES_4 + CASES_5

__all__ = ["CASES", "Case", "RiskSpec"]
