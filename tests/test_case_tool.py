import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).parents[1] / "skills" / "sudis-rebuttal-with-me" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from case_tool import (  # noqa: E402
    count_text,
    initialize_case,
    validate_case,
)


class CaseToolTests(unittest.TestCase):
    def test_initialize_case_creates_state_and_human_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)

            self.assertTrue((case_dir / "CASE_STATE.json").exists())
            self.assertTrue((case_dir / "ISSUE_BOARD.md").exists())
            self.assertTrue((case_dir / "EVIDENCE_LEDGER.md").exists())
            state = json.loads((case_dir / "CASE_STATE.json").read_text())
            self.assertEqual(state["schema_version"], "1.0")
            self.assertEqual(state["stage"], "intake")

    def test_strategy_gate_blocks_unknown_rules_and_untracked_issues(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            errors = validate_case(case_dir, "strategy")

            self.assertIn("official rules snapshot is missing", " ".join(errors))
            self.assertIn("no atomic reviewer issues are tracked", " ".join(errors))

    def test_count_text_reports_unicode_characters_and_words(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "text.txt"
            path.write_text("感谢 reviewer.\nAnswer: 42.", encoding="utf-8")

            self.assertEqual(count_text(path, "chars"), len(path.read_text()))
            self.assertEqual(count_text(path, "words"), 4)

    def test_paste_ready_gate_blocks_unconfirmed_evidence_links_and_em_dash(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(
                {
                    "stage": "draft",
                    "venue": {
                        "name": "ARR",
                        "rules_url": "https://aclrollingreview.org/authors",
                        "rules_fetched_at": "2026-07-10",
                        "limit_unit": "chars",
                        "limit_value": 5000,
                        "links_allowed": False,
                    },
                    "reviewers": [{"id": "R1"}],
                    "issues": [
                        {
                            "id": "R1-C1",
                            "reviewer_id": "R1",
                            "status": "answered",
                            "evidence_ids": ["E1"],
                            "commitment_ids": [],
                        }
                    ],
                    "evidence": [{"id": "E1", "status": "unverified"}],
                    "approvals": {
                        "strategy": "approved",
                        "facts": "pending",
                        "paste_ready": "pending",
                        "escalation": "not_requested",
                    },
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            (case_dir / "DRAFT.md").write_text(
                "Evidence: www.example.com — result is confirmed.\n"
            )

            errors = validate_case(case_dir, "paste-ready")
            joined = " ".join(errors)
            self.assertIn("unverified evidence", joined)
            self.assertIn("external links are not allowed", joined)
            self.assertIn("em dash", joined)
            self.assertIn("fact approval", joined)

    def test_complete_draft_passes_draft_gate_but_escalation_requires_mentor(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(
                {
                    "stage": "draft",
                    "venue": {
                        "name": "ICML",
                        "rules_url": "https://icml.cc/Conferences/2026/PeerReviewFAQ",
                        "rules_fetched_at": "2026-07-10",
                        "limit_unit": "chars",
                        "limit_value": 5000,
                        "links_allowed": True,
                    },
                    "reviewers": [{"id": "R1"}],
                    "issues": [
                        {
                            "id": "R1-C1",
                            "reviewer_id": "R1",
                            "status": "answered",
                            "evidence_ids": ["E1"],
                            "commitment_ids": [],
                        }
                    ],
                    "evidence": [{"id": "E1", "status": "author_confirmed"}],
                    "commitments": [],
                    "approvals": {
                        "strategy": "approved",
                        "facts": "approved",
                        "paste_ready": "pending",
                        "escalation": "pending",
                    },
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            (case_dir / "DRAFT.md").write_text("R1-C1: The confirmed result is 42.\n")
            (case_dir / "PASTE_READY.txt").write_text("R1-C1: The confirmed result is 42.\n")

            self.assertEqual(validate_case(case_dir, "draft"), [])
            state["approvals"]["paste_ready"] = "approved"
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            self.assertEqual(validate_case(case_dir, "paste-ready"), [])
            errors = validate_case(case_dir, "escalation")
            self.assertIn("mentor approval", " ".join(errors))

    def test_paste_ready_gate_requires_the_final_text_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(
                {
                    "venue": {
                        "rules_url": "https://example.org/rules",
                        "rules_fetched_at": "2026-07-10",
                        "limit_unit": "chars",
                        "limit_value": 100,
                        "links_allowed": True,
                    },
                    "reviewers": [{"id": "R1"}],
                    "issues": [
                        {
                            "id": "R1-C1",
                            "reviewer_id": "R1",
                            "status": "answered",
                            "evidence_ids": [],
                            "commitment_ids": [],
                        }
                    ],
                    "approvals": {
                        "strategy": "approved",
                        "facts": "approved",
                        "paste_ready": "approved",
                        "escalation": "not_requested",
                    },
                }
            )
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            (case_dir / "DRAFT.md").write_text("R1-C1: confirmed.\n")

            errors = validate_case(case_dir, "paste-ready")
            self.assertIn("PASTE_READY.txt is missing or empty", " ".join(errors))


if __name__ == "__main__":
    unittest.main()
