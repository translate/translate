import sys

import pytest

requires_py38_mark = pytest.mark.skipif(
    sys.version_info < (3, 8), reason="Requires python 3.8"
)

test_po_files = [
    "tests/cli/data/test_pocount_po_csv/one.po",
    "tests/cli/data/test_pocount_po_file/one.po",
    "tests/cli/data/test_pocount_po_fuzzy/one.po",
]
