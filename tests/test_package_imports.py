"""Task 0 — package skeleton import smoke tests."""

import fmea_agent
from fmea_agent import application, domain


def test_package_imports() -> None:
    assert fmea_agent.__version__ == "0.0.1"


def test_subpackages_import() -> None:
    assert domain.__name__ == "fmea_agent.domain"
    assert application.__name__ == "fmea_agent.application"
