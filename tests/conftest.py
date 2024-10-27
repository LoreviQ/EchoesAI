"""pytest config"""

import pytest


def pytest_addoption(parser):
    """Add option to run slow tests"""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config, items):
    """Skip slow tests if --runslow is not provided"""
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_configure(config):
    """Add custom markers to pytest"""
    config.addinivalue_line(
        "markers", "slow: mark test as slow and skipped unless --runslow is provided"
    )