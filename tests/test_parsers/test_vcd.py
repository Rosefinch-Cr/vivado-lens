"""Tests for VCD waveform parser."""

import pytest

from vivado_lens.parsers.vcd import parse_vcd


def test_parse_vcd_returns_waveform(vcd_path):
    if not vcd_path.exists():
        pytest.skip(f"VCD fixture not found: {vcd_path}")
    result = parse_vcd(vcd_path)
    assert result is not None


def test_signals_extracted(vcd_path):
    if not vcd_path.exists():
        pytest.skip("VCD fixture not found")
    result = parse_vcd(vcd_path)
    assert len(result.signals) > 0


def test_timescale_set(vcd_path):
    if not vcd_path.exists():
        pytest.skip("VCD fixture not found")
    result = parse_vcd(vcd_path)
    assert result.timescale != ""


def test_duration_positive(vcd_path):
    if not vcd_path.exists():
        pytest.skip("VCD fixture not found")
    result = parse_vcd(vcd_path)
    assert result.duration > 0


def test_signals_have_transitions(vcd_path):
    if not vcd_path.exists():
        pytest.skip("VCD fixture not found")
    result = parse_vcd(vcd_path)
    for sig in result.signals:
        assert len(sig.transitions) > 0
        for time, value in sig.transitions:
            assert time >= 0
            assert isinstance(value, int)


def test_signal_filter(vcd_path):
    if not vcd_path.exists():
        pytest.skip("VCD fixture not found")
    result = parse_vcd(vcd_path, signal_filter=["clk"])
    if result.signals:
        for sig in result.signals:
            assert "clk" in sig.name.lower()
