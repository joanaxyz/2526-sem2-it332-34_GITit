"""Exact ordered-output checks captured before the policy-module cutover."""

import sys
from pathlib import Path

_TEST_IMPORT_ROOT = Path(__file__).resolve().parents[4]
if str(_TEST_IMPORT_ROOT) not in sys.path:
    sys.path.insert(0, str(_TEST_IMPORT_ROOT))

from scripts.checks.architecture_guard.contracts.auth import (  # noqa: E402
    auth_secondary_backend_contract_violations,
)
from scripts.checks.architecture_guard.contracts.catalog import (  # noqa: E402
    catalog_secondary_backend_contract_violations,
)
from scripts.checks.architecture_guard.contracts.gameplay import (  # noqa: E402
    gameplay_mutation_frontend_violations,
)
from scripts.checks.architecture_guard.contracts.progress import (  # noqa: E402
    progress_summary_secondary_backend_contract_violations,
)

from .policy_equivalence_cases import (  # noqa: E402
    POLICY_EQUIVALENCE_CASES,
    PRE_CUTOVER_EXPECTED_VIOLATIONS,
)

del _TEST_IMPORT_ROOT


POLICY_FUNCTIONS = {
    "auth_secondary_backend_contract_violations": (auth_secondary_backend_contract_violations),
    "catalog_secondary_backend_contract_violations": (
        catalog_secondary_backend_contract_violations
    ),
    "gameplay_mutation_frontend_violations": gameplay_mutation_frontend_violations,
    "progress_summary_secondary_backend_contract_violations": (
        progress_summary_secondary_backend_contract_violations
    ),
}


def test_policy_modules_preserve_pre_cutover_ordered_violations():
    for domain, case in POLICY_EQUIVALENCE_CASES.items():
        actual = POLICY_FUNCTIONS[case["function"]](*case["args"])

        assert actual == PRE_CUTOVER_EXPECTED_VIOLATIONS[domain]
