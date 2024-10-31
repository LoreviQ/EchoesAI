"""pytest config"""

from typing import List

import pytest
from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.nodes import Item


def pytest_addoption(parser: Parser) -> None:
    """Add option to run slow tests"""
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_collection_modifyitems(config: Config, items: List[Item]) -> None:
    """Skip slow tests if --runslow is not provided"""
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


def pytest_configure(config: Config) -> None:
    """Add custom markers to pytest"""
    config.addinivalue_line(
        "markers", "slow: mark test as slow and skipped unless --runslow is provided"
    )
