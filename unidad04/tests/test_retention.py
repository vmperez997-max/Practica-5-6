from inf8239_u04.privacy import retention_plan


def test_retention_dry_run_keeps_hold_and_recent_records():
    records = [
        {"id": "old", "created_at": "2026-01-01"},
        {"id": "hold", "created_at": "2026-01-01", "hold": True},
        {"id": "recent", "created_at": "2026-10-20"},
    ]
    plan = retention_plan(records, "2026-10-23", 30)
    assert [r["action"] for r in plan] == ["REVIEW_FOR_DELETION", "HOLD", "KEEP"]
    assert all(r["dry_run"] for r in plan)
