def shifts(data):
    result = {}
    by_line = {}
    for row in data["shifts"]:
        if row["shift_id"] in result:
            raise ValueError("班次编号重复")
        if row["start_minute"] >= row["end_minute"]:
            raise ValueError("班次时间无效")
        if row["assigned"] not in {"standard", "fast"}:
            raise ValueError("未知运行安排")
        key = (row["line"], row["day"])
        for previous in by_line.get(key, []):
            if max(previous["start_minute"], row["start_minute"]) < min(previous["end_minute"], row["end_minute"]):
                raise ValueError("同线班次重叠")
        by_line.setdefault(key, []).append(row)
        result[row["shift_id"]] = dict(row)
    return result


def protocol(data, as_of):
    current = dict(data["protocol"])
    if current["signed_on"] > as_of:
        raise ValueError("该日期尚无已确认协议")
    current["closed"] = as_of >= current["close_on"]
    return current
