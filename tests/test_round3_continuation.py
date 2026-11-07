"""The continuation queue must not silently bypass a failed condition."""
import importlib.util


def module():
    spec = importlib.util.spec_from_file_location("continue_round3", "scripts/06_round3_continue.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def test_only_large_quality_failure_can_use_reviewed_fallback():
    record = dict(accepted=False, needs_large_fallback=True, small_quality_pass=True,
                  mechanism_pass=True, projected_expA_hours=20)
    m = module()
    assert m.next_action(record) == "fallback"
    assert m.next_action({**record, "small_quality_pass": False}) == "stop"
    assert m.next_action({**record, "mechanism_pass": False}) == "stop"
    assert m.next_action({**record, "projected_expA_hours": 37}) == "fallback"
    assert m.next_action({**record, "needs_large_fallback": False}) == "stop"


def test_only_accepted_evidence_starts_A():
    assert module().next_action(dict(accepted=True, mechanism_pass=True, source_quality_pass=True,
                                    small_quality_pass=True, projected_expA_hours=20)) == "run_A"
    assert module().next_action({"accepted": True}) == "stop"
    assert module().next_action({}) == "stop"
