"""Tests for timing report parser."""

from vivado_lens.parsers.timing import parse_timing_report


def test_parse_timing_returns_summary(timing_text):
    result = parse_timing_report(timing_text)
    assert result is not None


def test_clocks_extracted(timing_text):
    result = parse_timing_report(timing_text)
    assert len(result.clocks) >= 1
    clk = result.clocks[0]
    assert clk.period_ns > 0
    assert clk.frequency_mhz > 0


def test_slack_extracted(timing_text):
    result = parse_timing_report(timing_text)
    assert result.slack is not None
    assert result.slack.setup_ns != 0 or result.slack.hold_ns != 0


def test_slack_all_met_property(timing_text):
    """seq_det design should meet timing."""
    result = parse_timing_report(timing_text)
    assert result.slack.all_met is True
    assert result.slack.setup_failing == 0
    assert result.slack.hold_failing == 0
    assert result.slack.pw_failing == 0


def test_critical_path_extracted(timing_text):
    result = parse_timing_report(timing_text)
    assert result.critical_path is not None
    cp = result.critical_path
    assert cp.source != ""
    assert cp.destination != ""
    assert cp.data_path_delay_ns > 0
    assert 0 <= cp.logic_pct <= 100
    assert 0 <= cp.route_pct <= 100
    assert abs(cp.logic_pct + cp.route_pct - 100) < 1.0


def test_timing_met_property(timing_text):
    result = parse_timing_report(timing_text)
    assert result.timing_met is True


def test_empty_input_returns_empty_summary():
    result = parse_timing_report("")
    assert result.clocks == []
    assert result.slack is None
    assert result.critical_path is None
