"""Tests for log parser."""

from vivado_lens.parsers.log import extract_display_output, parse_vivado_log


def test_parse_log_basic():
    log = """
Phase 1: Init
Starting RTL Optimization
Finished RTL Optimization : Time (s): cpu = 00:00:01
WARNING: [Synth 8-1234] some warning
ERROR: [Synth 8-5678] something failed
Exiting Vivado
"""
    result = parse_vivado_log(log)
    assert len(result.errors) == 1
    assert "ERROR:" in result.errors[0]
    assert len(result.warnings) >= 1
    assert len(result.phases) >= 2


def test_log_success_property():
    log = "Starting synth\nFinished synth : Time"
    result = parse_vivado_log(log)
    assert result.success is True


def test_log_failure_property():
    log = "ERROR: [Synth 8-1234] failure"
    result = parse_vivado_log(log)
    assert result.success is False
    assert len(result.errors) == 1


def test_log_tail():
    lines = [f"line {i}" for i in range(50)]
    log = "\n".join(lines)
    result = parse_vivado_log(log, tail_lines=10)
    assert result.tail.count("\n") <= 10
    assert "line 49" in result.tail


def test_extract_display_output():
    xsim_log = """
Vivado Simulator 2017.4
Time resolution is 1 ps
INFO: [Common 17-206] Exiting Vivado
Test 1 PASS
Test 2 PASS
PASS: All tests passed!
"""
    output = extract_display_output(xsim_log)
    assert any("PASS" in line for line in output)
    assert all(not line.startswith("INFO:") for line in output)


def test_empty_log():
    result = parse_vivado_log("")
    assert result.errors == []
    assert result.warnings == []
    assert result.phases == []
    assert result.success is True
