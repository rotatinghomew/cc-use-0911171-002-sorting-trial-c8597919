import argparse
import json
from pathlib import Path
from records import load, save


def inspect(data, as_of):
    from schedule import protocol
    from production import adherence
    from quality import operational_totals, audit_checks
    return {"protocol": protocol(data, as_of), "adherence": adherence(data, as_of),
            "inspection_audit": audit_checks(data, as_of), "operational": operational_totals(data, as_of)}



def main():
    parser = argparse.ArgumentParser(description="分拣班次排程、实际运行和质量检验合格产出核对。")
    parser.add_argument("action", choices=["demo", "inspect"])
    parser.add_argument("--data", type=Path, default=Path(__file__).parent / "fixtures/data.json")
    parser.add_argument("--as-of", default="2026-10-18")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = inspect(load(args.data), args.as_of)
    if args.output:
        save(args.output, result)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
