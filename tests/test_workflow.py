import copy
import json
import unittest
from pathlib import Path
from app import inspect
from records import load


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.data = copy.deepcopy(load(Path(__file__).parents[1] / "fixtures/data.json"))
        self.day = "2026-10-18"

    def test_end_to_end_inspection_is_json_and_repeatable(self):
        before = copy.deepcopy(self.data)
        first = inspect(self.data, self.day)
        self.assertEqual(first, inspect(self.data, self.day))
        self.assertEqual(before, self.data)
        self.assertTrue(json.dumps(first, ensure_ascii=False, allow_nan=False))

    def test_assignments_and_execution_are_separate(self):
        from production import adherence
        rows = adherence(self.data, self.day)
        self.assertTrue(any(row["deviations"] for row in rows.values()))

    def test_pending_is_not_qualified(self):
        from quality import reconciled
        rows = reconciled(self.data, "2026-10-04")
        self.assertTrue(any(row["quality"] == "pending" for row in rows))
        self.assertTrue(all(row["qualified_kg"] is None for row in rows if row["quality"] == "pending"))

    def test_late_quality_changes_totals(self):
        from quality import operational_totals
        early = operational_totals(self.data, "2026-10-16")
        late = operational_totals(self.data, "2026-10-18")
        self.assertEqual(early["L1"]["output_kg"], late["L1"]["output_kg"])
        self.assertGreaterEqual(late["L1"]["qualified_kg"], early["L1"]["qualified_kg"])

    def test_protocol_close_is_date_based(self):
        from schedule import protocol
        self.assertFalse(protocol(self.data, "2026-10-18")["closed"])
        self.assertTrue(protocol(self.data, "2026-10-21")["closed"])

    def test_overlapping_shift_rejected(self):
        from schedule import shifts
        self.data["shifts"].append({**self.data["shifts"][0], "shift_id": "duplicate-time"})
        with self.assertRaises(ValueError):
            shifts(self.data)

    def test_carryover_is_retained(self):
        from production import runs
        self.assertTrue(any(row["outside_shift"] for row in runs(self.data, self.day)["runs"]))

    def test_rechecks_have_visible_initial_evidence(self):
        from quality import audit_checks
        evidence = audit_checks(self.data, self.day)
        self.assertTrue(evidence["rechecks"])
        self.assertEqual(evidence["orphan_rechecks"], [])
