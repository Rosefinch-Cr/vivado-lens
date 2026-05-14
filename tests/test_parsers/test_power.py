"""Tests for power report parser."""

from vivado_lens.parsers.power import parse_power_report


def test_parse_power_returns_result(power_text):
    result = parse_power_report(power_text)
    assert result is not None


def test_total_power_extracted(power_text):
    result = parse_power_report(power_text)
    assert result.total_w > 0


def test_dynamic_static_split(power_text):
    result = parse_power_report(power_text)
    assert result.dynamic_w >= 0
    assert result.static_w >= 0
    assert result.total_w >= result.dynamic_w
    assert result.total_w >= result.static_w


def test_junction_temp_extracted(power_text):
    result = parse_power_report(power_text)
    assert result.junction_temp_c > 0
    assert result.junction_temp_c < 200  # sanity


def test_confidence_extracted(power_text):
    result = parse_power_report(power_text)
    assert result.confidence in ("Low", "Medium", "High")


def test_empty_input_returns_zeros():
    result = parse_power_report("")
    assert result.total_w == 0.0
    assert result.dynamic_w == 0.0
    assert result.static_w == 0.0
    assert result.components == []
