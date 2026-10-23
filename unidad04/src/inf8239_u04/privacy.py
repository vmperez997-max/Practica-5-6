from datetime import datetime


def retention_plan(records, as_of, days):
    """Dry run only: preserve legal holds and never silently delete evidence."""
    if days < 1:
        raise ValueError("Positive retention days required")
    now = datetime.fromisoformat(as_of)
    plan = []
    for record in records:
        created = datetime.fromisoformat(record["created_at"])
        age = (now - created).days
        action = (
            "HOLD"
            if record.get("hold", False)
            else "REVIEW_FOR_DELETION"
            if age > days
            else "KEEP"
        )
        plan.append(
            {"id": record["id"], "age_days": age, "action": action, "dry_run": True}
        )
    return plan
