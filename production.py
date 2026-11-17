from records import latest, quantity
from schedule import shifts


def runs(data, as_of):
    planned = shifts(data)
    accepted, unknown = [], []
    for row in latest(data["batches"], "batch_id", as_of):
        shift = planned.get(row["shift_id"])
        if shift is None:
            unknown.append(row["batch_id"])
            continue
        if shift["day"] > as_of:
            continue
        minutes = quantity(row["minutes"])
        if not minutes:
            raise ValueError("运行时长必须大于零")
        output = quantity(row["output_kg"])
        if output > quantity(row["input_kg"]):
            raise ValueError("产出超过投入")
        accepted.append({**row, "assigned": shift["assigned"], "line": shift["line"],
                         "outside_shift": not shift["start_minute"] <= row["arrival_minute"] < shift["end_minute"],
                         "kg_per_hour": output * 60 / minutes})
    return {"runs": accepted, "unknown_batches": unknown}


def adherence(data, as_of):
    result = {}
    for row in runs(data, as_of)["runs"]:
        group = result.setdefault(row["shift_id"], {"assigned": row["assigned"], "batches": 0, "deviations": 0})
        group["batches"] += 1
        group["deviations"] += row["assigned"] != row["run_mode"]
    return result
