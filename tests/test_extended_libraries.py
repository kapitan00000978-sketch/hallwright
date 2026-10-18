"""
Tests for extended enterprise domain libraries:
- SagaCoordinator
- OwaspGuard
- WorkQueue
- SqlInjectionDetector
- ChaosInjector
"""

import time
import pytest
from src.libraries.architecture.saga_coordinator import SagaCoordinator, SagaState, SagaStepStatus
from src.libraries.security.owasp_guard import OwaspGuard, scan_source_for_owasp_risks
from src.libraries.performance.work_queue import WorkQueue
from src.libraries.database.sqli_neutralizer import SqlInjectionDetector, audit_sql_injections
from src.libraries.resilience.chaos_injector import (
    ChaosInjector,
    ChaosFault,
    LatencyChaosFault,
)


def test_saga_coordinator_success():
    saga = SagaCoordinator(name="test_order_saga")
    trace = []

    def step1(ctx):
        trace.append("step1")
        return {"order_id": 101}

    def step2(ctx):
        trace.append(f"step2_with_{ctx['order_id']}")
        return {"payment_id": 202}

    saga.add_step("create_order", step1, lambda ctx: trace.append("compensate_1"))
    saga.add_step("process_payment", step2, lambda ctx: trace.append("compensate_2"))

    success = saga.execute({"user": "alice"})
    assert success is True
    assert saga.state == SagaState.SUCCESS
    assert trace == ["step1", "step2_with_101"]
    summary = saga.get_summary()
    assert summary["step_count"] == 2
    assert summary["state"] == "success"


def test_saga_coordinator_rollback_on_failure():
    saga = SagaCoordinator(name="test_failure_saga")
    trace = []

    def step1(ctx):
        trace.append("step1")
        return {"inventory_reserved": True}

    def comp1(ctx):
        trace.append("rollback_inventory")

    def step2(ctx):
        trace.append("step2_fail")
        raise RuntimeError("Payment gateway unavailable")

    def comp2(ctx):
        trace.append("rollback_payment")

    saga.add_step("reserve_inventory", step1, comp1)
    saga.add_step("charge_card", step2, comp2)

    success = saga.execute({})
    assert success is False
    assert saga.state == SagaState.ROLLED_BACK
    assert "step1" in trace
    assert "step2_fail" in trace
    assert "rollback_inventory" in trace
    # Step 2 never succeeded, so its compensation is not called
    assert "rollback_payment" not in trace


def test_owasp_guard_detections():
    vulnerable_code = (
        'import os, pickle, yaml\n'
        'os.system("rm -rf " + path)\n'
        'subprocess.run("ls", shell=True)\n'
        'pickle.loads(payload)\n'
        'yaml.load(stream)\n'
        'eval("dangerous()")\n'  # hallwright-ignore
    )

    guard = OwaspGuard(filename="sample_vuln.py")
    vulns = guard.audit_source(vulnerable_code)
    rule_ids = [v.rule_id for v in vulns]

    assert "INSECURE_OS_EXEC" in rule_ids
    assert "COMMAND_INJECTION_SHELL_TRUE" in rule_ids
    assert "INSECURE_PICKLE_DESERIALIZATION" in rule_ids
    assert "INSECURE_YAML_LOAD" in rule_ids
    assert "DYNAMIC_EVAL_EXEC" in rule_ids

    # Helper function check
    serialized = scan_source_for_owasp_risks(vulnerable_code)
    assert len(serialized) >= 5


def test_work_queue_execution_and_priority():
    queue = WorkQueue(max_workers=2)
    results = []

    def task(val):
        results.append(val)
        return val * 2

    # Higher priority (lower number) should execute first if queued
    item1 = queue.submit(task, 10, priority=1)
    item2 = queue.submit(task, 20, priority=5)

    assert item1.wait(timeout=2.0) == 20
    assert item2.wait(timeout=2.0) == 40

    stats = queue.get_stats()
    assert stats["processed_items"] >= 2
    assert stats["active_workers"] == 2
    queue.shutdown(wait=True)


def test_sqli_neutralizer_detections():
    insecure_code = (
        'def get_user(db, user_id, col):\n'
        '    db.execute(f"SELECT * FROM users WHERE id = {user_id}")\n'
        '    db.execute("SELECT " + col + " FROM users")\n'
        '    db.execute("SELECT * FROM accounts WHERE name = \'%s\'" % user_id)\n'
    )

    detector = SqlInjectionDetector(file_path="repo.py")
    findings = detector.check_source(insecure_code)
    assert len(findings) == 3
    assert all(f.risk_level == "CRITICAL" for f in findings)

    summary = audit_sql_injections(insecure_code)
    assert len(summary) == 3


def test_chaos_injector_behavior():
    injector = ChaosInjector(enabled=True, seed=42)

    # Probabilistic fault injection
    triggered = False
    for _ in range(100):
        try:
            injector.maybe_inject_fault(probability=0.5, fault_type=ChaosFault)
        except ChaosFault:
            triggered = True
            break
    assert triggered is True

    # Scoped fault
    with pytest.raises(LatencyChaosFault):
        with injector.fault_scope(fault_type=LatencyChaosFault, message="Latency spike"):
            pass

    # Wrap decorator
    @injector.wrap(probability=1.0, fault_type=ChaosFault)
    def fragile_function():
        return "unreachable"

    with pytest.raises(ChaosFault):
        fragile_function()

    stats = injector.get_stats()
    assert stats["enabled"] is True
    assert stats["total_faults_triggered"] >= 2
