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


def ready_neurips_state(track="main", phase="initial_response", reviewers=None):
    reviewers = reviewers or ["R1"]
    profile_id = "neurips-2026-ed" if track == "evaluations_and_datasets" else "neurips-2026-main"
    reviewer_records = [
        {
            "id": reviewer_id,
            "lane": "positive-conditional",
            "support": "high",
            "persuadability": "high",
            "decision_relevance": "high",
            "addressability": "existing_evidence",
        }
        for reviewer_id in reviewers
    ]
    issues = [
        {
            "id": f"{reviewer_id}-C1",
            "reviewer_id": reviewer_id,
            "status": "answered",
            "stance_signal": "positive",
            "evidence_ids": ["E1"],
            "commitment_ids": [],
        }
        for reviewer_id in reviewers
    ]
    return {
        "intake_mode": "local_markdown",
        "paper_status": "provided",
        "raw_review_status": "confirmed",
        "venue": {
            "name": "NeurIPS",
            "cycle": "2026",
            "track": track,
            "profile": "neurips",
            "rules_url": "https://neurips.cc/Conferences/2026/MainTrackHandbook",
            "rules_fetched_at": "2026-07-22",
            "rules_profile_id": profile_id,
            "rules_status": "current_official",
            "response_mode": "per_review_openreview",
            "limit_scope": "per_review",
            "limit_unit": "chars",
            "limit_value": 10000,
            "links_allowed": False,
            "files_allowed": False,
            "paper_revision_allowed": False,
            "new_results_policy": "direct_response_allowed_submission_remains_basis",
            "neurips": {
                "phase": phase,
                "initial_meta_review_status": "provided",
                "contribution_type": "datasets_and_data_resources" if track == "evaluations_and_datasets" else "general",
                "response_files": {reviewer_id: f"NEURIPS_RESPONSES/{reviewer_id}.md" for reviewer_id in reviewers},
            },
        },
        "reviewers": reviewer_records,
        "issues": issues,
        "evidence": [{"id": "E1", "status": "author_confirmed", "origin": "paper"}],
        "approvals": {
            "strategy": "approved",
            "facts": "approved",
            "paste_ready": "approved",
            "escalation": "not_requested",
        },
    }


class CaseToolTests(unittest.TestCase):
    def test_initialize_case_creates_state_and_human_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)

            self.assertTrue((case_dir / "CASE_STATE.json").exists())
            self.assertTrue((case_dir / "ISSUE_BOARD.md").exists())
            self.assertTrue((case_dir / "REVIEWER_LANES.md").exists())
            self.assertTrue((case_dir / "ARR_THREAD_PLAN.md").exists())
            self.assertTrue((case_dir / "ARR_ISSUE_REPORT.md").exists())
            self.assertTrue((case_dir / "AC_SUMMARY.md").exists())
            self.assertTrue((case_dir / "AC_MESSAGE.md").exists())
            self.assertTrue((case_dir / "CASE_INTAKE.md").exists())
            self.assertTrue((case_dir / "REVIEWS_INPUT.md").exists())
            self.assertIn("complete raw OpenReview", (case_dir / "REVIEWS_INPUT.md").read_text())
            self.assertTrue((case_dir / "EVIDENCE_LEDGER.md").exists())
            state = json.loads((case_dir / "CASE_STATE.json").read_text())
            self.assertEqual(state["schema_version"], "1.0")
            self.assertEqual(state["stage"], "intake")

    def test_neurips_initialization_is_profile_specific(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir, profile="neurips", track="main", cycle="2026")

            self.assertTrue((case_dir / "NEURIPS_META_REVIEW_MAP.md").exists())
            self.assertTrue((case_dir / "NEURIPS_THREAD_PLAN.md").exists())
            self.assertTrue((case_dir / "NEURIPS_RESPONSES").is_dir())
            self.assertFalse((case_dir / "ARR_THREAD_PLAN.md").exists())
            state = json.loads((case_dir / "CASE_STATE.json").read_text())
            self.assertEqual(state["venue"]["profile"], "neurips")
            self.assertEqual(state["venue"]["track"], "main")

    def test_neurips_future_cycle_is_triage_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir, profile="neurips", track="main", cycle="2027")
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(ready_neurips_state())
            state["venue"].update({
                "cycle": "2027",
                "rules_profile_id": "",
                "rules_status": "future_unpublished",
            })
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            errors = validate_case(case_dir, "strategy")
            self.assertIn("NeurIPS future rules are unpublished; triage only", errors)

    def test_neurips_paste_ready_counts_each_reviewer_independently(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir, profile="neurips", track="main", cycle="2026")
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(ready_neurips_state(reviewers=["R1", "R2"]))
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            (case_dir / "DRAFT.md").write_text("Reviewed draft.\n")
            for reviewer_id in ("R1", "R2"):
                (case_dir / "NEURIPS_RESPONSES" / f"{reviewer_id}.md").write_text("a" * 9000)
            (case_dir / "PASTE_READY.md").write_text("R1: 9000 chars\nR2: 9000 chars\n")

            self.assertEqual(validate_case(case_dir, "paste-ready"), [])

    def test_neurips_paste_ready_blocks_over_limit_link_and_scope_expansion(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir, profile="neurips", track="main", cycle="2026")
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(ready_neurips_state())
            state["evidence"] = [{"id": "E1", "status": "author_confirmed", "origin": "major_scope_change"}]
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            (case_dir / "DRAFT.md").write_text("Reviewed draft.\n")
            (case_dir / "NEURIPS_RESPONSES" / "R1.md").write_text("https://example.org\n" + "a" * 10001)
            (case_dir / "PASTE_READY.md").write_text("R1: pending\n")

            errors = " ".join(validate_case(case_dir, "paste-ready"))
            self.assertIn("scope-expanding NeurIPS evidence", errors)
            self.assertIn("external links are not allowed", errors)
            self.assertIn("exceeds the chars limit", errors)

    def test_neurips_blocks_author_reply_after_author_visibility_closes(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir, profile="neurips", track="evaluations_and_datasets", cycle="2026")
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(ready_neurips_state(track="evaluations_and_datasets", phase="reviewer_ac_only"))
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            (case_dir / "DRAFT.md").write_text("Reviewed draft.\n")
            (case_dir / "NEURIPS_RESPONSES" / "R1.md").write_text("Confirmed response.\n")
            (case_dir / "PASTE_READY.md").write_text("R1: 19 chars\n")

            errors = " ".join(validate_case(case_dir, "paste-ready"))
            self.assertIn("authors cannot post responses", errors)

    def test_neurips_ed_requires_an_ed_contribution_type(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir, profile="neurips", track="evaluations_and_datasets", cycle="2026")
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(ready_neurips_state(track="evaluations_and_datasets"))
            state["venue"]["neurips"]["contribution_type"] = "general"
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))

            errors = " ".join(validate_case(case_dir, "strategy"))
            self.assertIn("contribution_type is missing or invalid", errors)

    def test_strategy_gate_blocks_unknown_rules_and_untracked_issues(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            errors = validate_case(case_dir, "strategy")

            self.assertIn("official rules snapshot is missing", " ".join(errors))
            self.assertIn("no atomic reviewer issues are tracked", " ".join(errors))

    def test_url_only_intake_is_triage_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update({
                "intake_mode": "url_reference_only",
                "paper_status": "provided",
                "raw_review_status": "unknown",
                "venue": {"rules_url": "https://example.org/rules", "rules_fetched_at": "2026-07-10"},
                "reviewers": [{"id": "R1", "lane": "unknown-insufficient", "support": "unknown", "persuadability": "unknown", "decision_relevance": "unknown", "addressability": "unknown"}],
                "issues": [{"id": "R1-C1", "reviewer_id": "R1", "status": "needs_user_input", "stance_signal": "unknown"}],
            })
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            errors = validate_case(case_dir, "strategy")
            self.assertIn("URL-only intake is triage-only", " ".join(errors))

    def test_arr_strategy_gate_requires_current_profile_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state["venue"].update({"profile": "arr", "rules_url": "https://aclrollingreview.org/authors", "rules_fetched_at": "2026-07-10"})
            state.update({"intake_mode": "local_markdown", "paper_status": "provided", "raw_review_status": "confirmed"})
            state["reviewers"] = [{"id": "R1", "lane": "positive-champion", "support": "high", "persuadability": "medium", "decision_relevance": "high", "addressability": "existing_evidence"}]
            state["issues"] = [{"id": "R1-C1", "reviewer_id": "R1", "status": "open", "stance_signal": "positive"}]
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            errors = validate_case(case_dir, "strategy")
            joined = " ".join(errors)
            self.assertIn("ARR response mode", joined)
            self.assertIn("ARR limit status", joined)

    def test_arr_paste_ready_blocks_unsolicited_new_results(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update({
                "intake_mode": "local_markdown",
                "paper_status": "provided",
                "raw_review_status": "confirmed",
                "venue": {
                    "name": "ARR", "profile": "arr", "rules_url": "https://aclrollingreview.org/authors",
                    "rules_fetched_at": "2026-07-10", "response_mode": "text_only",
                    "limit_status": "officially_unspecified", "links_allowed": False,
                    "new_results_policy": "direct_minor_add_on_only",
                },
                "reviewers": [{"id": "R1", "lane": "negative-addressable", "support": "low", "persuadability": "high", "decision_relevance": "high", "addressability": "small_add_on"}],
                "issues": [{"id": "R1-C1", "reviewer_id": "R1", "status": "answered", "stance_signal": "negative", "evidence_ids": ["E1"], "commitment_ids": []}],
                "evidence": [{"id": "E1", "status": "author_confirmed", "origin": "unsolicited_new"}],
                "approvals": {"strategy": "approved", "facts": "approved", "paste_ready": "approved", "escalation": "not_requested"},
            })
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            (case_dir / "DRAFT.md").write_text("R1-C1: confirmed.\n")
            (case_dir / "PASTE_READY.md").write_text("R1-C1: confirmed.\n")
            errors = validate_case(case_dir, "paste-ready")
            self.assertIn("unsolicited or substantial new results", " ".join(errors))

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
                    "intake_mode": "local_markdown",
                    "paper_status": "provided",
                    "raw_review_status": "confirmed",
                    "stage": "draft",
                    "venue": {
                        "name": "ARR",
                        "rules_url": "https://aclrollingreview.org/authors",
                        "rules_fetched_at": "2026-07-10",
                        "limit_unit": "chars",
                        "limit_value": 5000,
                        "links_allowed": False,
                    },
                    "reviewers": [{"id": "R1", "lane": "positive-champion", "support": "high", "persuadability": "medium", "decision_relevance": "high", "addressability": "existing_evidence"}],
                    "issues": [
                        {
                            "id": "R1-C1",
                            "reviewer_id": "R1",
                            "status": "answered",
                            "evidence_ids": ["E1"],
                            "commitment_ids": [],
                            "stance_signal": "positive",
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

    def test_paste_ready_gate_blocks_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update({
                "intake_mode": "local_markdown",
                "paper_status": "provided",
                "raw_review_status": "confirmed",
                "venue": {"rules_url": "https://example.org/rules", "rules_fetched_at": "2026-07-10", "links_allowed": True},
                "reviewers": [{"id": "R1", "lane": "positive-champion", "support": "high", "persuadability": "medium", "decision_relevance": "high", "addressability": "existing_evidence"}],
                "issues": [{"id": "R1-C1", "reviewer_id": "R1", "status": "answered", "stance_signal": "positive", "evidence_ids": [], "commitment_ids": []}],
                "approvals": {"strategy": "approved", "facts": "approved", "paste_ready": "approved", "escalation": "not_requested"},
            })
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            (case_dir / "DRAFT.md").write_text("R1-C1: confirmed.\n")
            (case_dir / "PASTE_READY.md").write_text("TODO: add the confirmed result.\n")
            errors = validate_case(case_dir, "paste-ready")
            self.assertIn("unresolved placeholder", " ".join(errors))

    def test_complete_draft_passes_draft_gate_but_escalation_requires_mentor(self):
        with tempfile.TemporaryDirectory() as tmp:
            case_dir = Path(tmp) / "case"
            initialize_case(case_dir)
            state_path = case_dir / "CASE_STATE.json"
            state = json.loads(state_path.read_text())
            state.update(
                {
                    "intake_mode": "local_markdown",
                    "paper_status": "provided",
                    "raw_review_status": "confirmed",
                    "stage": "draft",
                    "venue": {
                        "name": "ICML",
                        "rules_url": "https://icml.cc/Conferences/2026/PeerReviewFAQ",
                        "rules_fetched_at": "2026-07-10",
                        "limit_unit": "chars",
                        "limit_value": 5000,
                        "links_allowed": True,
                    },
                    "reviewers": [{"id": "R1", "lane": "positive-champion", "support": "high", "persuadability": "medium", "decision_relevance": "high", "addressability": "existing_evidence"}],
                    "issues": [
                        {
                            "id": "R1-C1",
                            "reviewer_id": "R1",
                            "status": "answered",
                            "evidence_ids": ["E1"],
                            "commitment_ids": [],
                            "stance_signal": "positive",
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
            (case_dir / "PASTE_READY.md").write_text("R1-C1: The confirmed result is 42.\n")

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
                    "intake_mode": "local_markdown",
                    "paper_status": "provided",
                    "raw_review_status": "confirmed",
                    "venue": {
                        "rules_url": "https://example.org/rules",
                        "rules_fetched_at": "2026-07-10",
                        "limit_unit": "chars",
                        "limit_value": 100,
                        "links_allowed": True,
                    },
                    "reviewers": [{"id": "R1", "lane": "positive-champion", "support": "high", "persuadability": "medium", "decision_relevance": "high", "addressability": "existing_evidence"}],
                    "issues": [
                        {
                            "id": "R1-C1",
                            "reviewer_id": "R1",
                            "status": "answered",
                            "evidence_ids": [],
                            "commitment_ids": [],
                            "stance_signal": "positive",
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
            self.assertIn("PASTE_READY.md is missing or empty", " ".join(errors))


if __name__ == "__main__":
    unittest.main()
