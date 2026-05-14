"""Tests for utilization report parser."""

from vivado_lens.parsers.utilization import parse_utilization_report


def test_parse_utilization_returns_result(utilization_text):
    result = parse_utilization_report(utilization_text)
    assert result is not None


def test_slice_logic_extracted(utilization_text):
    result = parse_utilization_report(utilization_text)
    assert len(result.slice_logic) > 0


def test_resource_fields_valid(utilization_text):
    result = parse_utilization_report(utilization_text)
    for r in result.slice_logic:
        assert r.name != ""
        assert r.used >= 0
        assert r.available > 0
        assert 0 <= r.utilization_pct <= 100


def test_lut_usage_present(utilization_text):
    """seq_det should use at least 1 LUT."""
    result = parse_utilization_report(utilization_text)
    lut_entries = [r for r in result.slice_logic if "LUT" in r.name]
    assert len(lut_entries) > 0
    assert any(r.used > 0 for r in lut_entries)


def test_ff_usage_present(utilization_text):
    """seq_det FSM has 3 state bits = at least 3 FFs."""
    result = parse_utilization_report(utilization_text)
    ff_entries = [r for r in result.slice_logic
                  if "Register" in r.name or "Flip Flop" in r.name]
    assert len(ff_entries) > 0
    assert any(r.used >= 3 for r in ff_entries)


def test_empty_input_returns_empty_result():
    result = parse_utilization_report("")
    assert result.slice_logic == []
    assert result.memory == []
    assert result.dsp == []
    assert result.io == []
