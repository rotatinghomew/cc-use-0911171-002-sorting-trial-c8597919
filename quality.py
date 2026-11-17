from production import runs
from records import latest, quantity


def reconciled(data, as_of):
    checks = {row["batch_id"]: row for row in latest(data["inspections"], "inspection_id", as_of)}
    results = []
    for row in runs(data, as_of)["runs"]:
        check = checks.get(row["batch_id"])
        if check is None or check["status"] != "final":
            results.append({**row, "quality": "pending", "qualified_kg": None})
            continue
        checked = quantity(check["checked_kg"])
        damaged = quantity(check["damaged_kg"])
        if checked == 0 or damaged > checked:
            raise ValueError("质量检验分子分母无效")
        results.append({**row, "quality": "final", "damage_rate": damaged / checked,
                        "qualified_kg": row["output_kg"] * (1 - damaged / checked)})
    return results


def operational_totals(data, as_of):
    totals = {}
    for row in reconciled(data, as_of):
        group = totals.setdefault(row["line"], {"output_kg": 0, "qualified_kg": 0, "pending_batches": 0})
        group["output_kg"] += row["output_kg"]
        group["pending_batches"] += row["quality"] == "pending"
        if row["qualified_kg"] is not None:
            group["qualified_kg"] += row["qualified_kg"]
    return totals


def audit_checks(data, as_of):
    initial = latest(data["inspections"], "inspection_id", as_of)
    rechecks = latest(data["rechecks"], "recheck_id", as_of)
    known = {row["inspection_id"] for row in initial}
    orphans = [row["recheck_id"] for row in rechecks if row["inspection_id"] not in known]
    return {"initial_checks": initial, "rechecks": rechecks, "orphan_rechecks": orphans,
            "calibration_counts": data["calibration"]}
