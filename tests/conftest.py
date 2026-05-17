from __future__ import annotations

import pytest


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.pluginmanager.hasplugin("syrupy"):
        return

    snapshot_tests = [
        item.nodeid for item in items if "snapshot" in getattr(item, "fixturenames", ())
    ]
    if not snapshot_tests:
        return

    examples = "\n".join(f"  - {nodeid}" for nodeid in snapshot_tests[:5])
    raise pytest.UsageError(
        "The pytest 'snapshot' fixture is provided by the syrupy plugin, but "
        "syrupy is not installed or the plugin is not loaded.\n"
        "Install test dependencies with `uv sync --all-extras --dev`, or add "
        "the equivalent distro package for syrupy to checkdepends.\n"
        f"{len(snapshot_tests)} collected test(s) require it, for example:\n"
        f"{examples}"
    )
