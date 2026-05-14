"""Shared pytest fixtures for vivado-lens tests."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def timing_text() -> str:
    return (FIXTURES_DIR / "timing_summary.rpt").read_text(errors="replace")


@pytest.fixture(scope="session")
def utilization_text() -> str:
    return (FIXTURES_DIR / "utilization.rpt").read_text(errors="replace")


@pytest.fixture(scope="session")
def power_text() -> str:
    return (FIXTURES_DIR / "power.rpt").read_text(errors="replace")


@pytest.fixture(scope="session")
def vcd_path() -> Path:
    return FIXTURES_DIR / "sample.vcd"
