#!/usr/bin/env python3
"""Deterministic checks for a structured rebuttal case workspace.

The script deliberately does not fetch venues, run experiments, or generate prose.
It only creates templates, counts text, and blocks unsafe workflow transitions.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ARTIFACT_TEMPLATES = {
    "RULES_SNAPSHOT.md": "# Rules Snapshot\n\nRecord the official venue rules, URL, fetch date, and relevant excerpts.\n",
    "ISSUE_BOARD.md": "# Issue Board\n\nRecord one atomic issue per row and link it to evidence and commitments.\n",
    "REVIEWER_LANES.md": "# Reviewer Lanes\n\nRecord exactly one current lane per reviewer and preserve issue-level stance separately.\n",
    "EVIDENCE_LEDGER.md": "# Evidence Ledger\n\nRecord the source and confirmation status of every factual claim.\n",
    "STRATEGY.md": "# Strategy\n\nState the structured expert outlook, priorities, risks, and approval status.\n",
    "DRAFT.md": "# Draft\n\nKeep reviewer-facing text here until facts and commitments are confirmed.\n",
    "PASTE_READY.txt": "",
    "REVISION_PLAN.md": "# Revision Plan\n\nMap every paper-edit promise to an issue ID and commitment status.\n",
    "FOLLOWUP_LOG.md": "# Follow-up Log\n\nAppend new comments, delta replies, and approval records.\n",
}


DEFAULT_STATE: dict[str, Any] = {
    "schema_version": "1.0",
    "case_id": "",
    "stage": "intake",
    "venue": {
        "name": "",
        "cycle": "",
        "track": "",
        "rules_url": "",
        "rules_fetched_at": "",
        "limit_unit": "",
        "limit_value": None,
        "links_allowed": False,
        "new_results_policy": "unknown",
    },
    "deadlines": {},
    "reviewers": [],
    "issues": [],
    "evidence": [],
    "commitments": [],
    "approvals": {
        "strategy": "pending",
        "facts": "pending",
        "paste_ready": "pending",
        "escalation": "not_requested",
    },
}

LANES = {
    "positive-champion",
    "positive-conditional",
    "mixed-swing",
    "negative-addressable",
    "negative-fundamental",
    "negative-procedural-risk",
    "unknown-insufficient",
}
SCALE_DIMENSIONS = {"high", "medium", "low", "unknown"}
ADDRESSABILITY = {"existing_evidence", "small_add_on", "paper_revision", "unsupported_now", "unknown"}


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def initialize_case(case_dir: Path) -> None:
    """Create a case workspace without overwriting existing files."""

    case_dir = Path(case_dir)
    case_dir.mkdir(parents=True, exist_ok=True)
    state_path = case_dir / "CASE_STATE.json"
    if not state_path.exists():
        _write_json(state_path, DEFAULT_STATE)
    for filename, content in ARTIFACT_TEMPLATES.items():
        path = case_dir / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def count_text(path: Path, unit: str) -> int:
    text = Path(path).read_text(encoding="utf-8")
    if unit == "chars":
        return len(text)
    if unit == "words":
        return len(re.findall(r"\S+", text))
    raise ValueError(f"unsupported unit: {unit}")


def _load_state(case_dir: Path) -> tuple[dict[str, Any] | None, list[str]]:
    path = Path(case_dir) / "CASE_STATE.json"
    if not path.exists():
        return None, ["CASE_STATE.json is missing"]
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"CASE_STATE.json is invalid JSON: {exc}"]
    if not isinstance(value, dict):
        return None, ["CASE_STATE.json must contain an object"]
    return value, []


def _venue_rules_errors(state: dict[str, Any]) -> list[str]:
    venue = state.get("venue") or {}
    errors: list[str] = []
    if not venue.get("rules_url") or not venue.get("rules_fetched_at"):
        errors.append("official rules snapshot is missing")
    return errors


def _issue_errors(state: dict[str, Any]) -> list[str]:
    reviewers = state.get("reviewers") or []
    issues = state.get("issues") or []
    errors: list[str] = []
    if not reviewers:
        errors.append("reviewer records are missing")
    if not issues:
        errors.append("no atomic reviewer issues are tracked")
    reviewer_ids = {r.get("id") for r in reviewers if isinstance(r, dict)}
    for reviewer in reviewers:
        if not isinstance(reviewer, dict):
            errors.append("a reviewer record is not an object")
            continue
        reviewer_id = reviewer.get("id", "<unnamed reviewer>")
        if reviewer.get("lane") not in LANES:
            errors.append(f"{reviewer_id} has no valid reviewer lane")
        for dimension in ("support", "persuadability", "decision_relevance"):
            if reviewer.get(dimension) not in SCALE_DIMENSIONS:
                errors.append(f"{reviewer_id} has no valid {dimension} dimension")
        if reviewer.get("addressability") not in ADDRESSABILITY:
            errors.append(f"{reviewer_id} has no valid addressability dimension")
    for issue in issues:
        if not isinstance(issue, dict):
            errors.append("an issue record is not an object")
            continue
        issue_id = issue.get("id", "<unnamed issue>")
        if issue.get("reviewer_id") not in reviewer_ids:
            errors.append(f"{issue_id} references an unknown reviewer")
        if not issue.get("status"):
            errors.append(f"{issue_id} has no status")
        if issue.get("stance_signal") not in {"positive", "mixed", "negative", "unknown"}:
            errors.append(f"{issue_id} has no valid stance_signal")
    return errors


def _text_errors(path: Path, venue: dict[str, Any], label: str) -> list[str]:
    if not path.exists() or not path.read_text(encoding="utf-8").strip():
        return [f"{label} is missing or empty"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    if not venue.get("links_allowed", False) and re.search(r"https?://|www\.", text, re.I):
        errors.append("external links are not allowed")
    if "—" in text or "---" in text:
        errors.append("em dash or triple-hyphen punctuation is not allowed in English draft text")
    if re.search(r"\b(?:TODO|TBD|FIXME|<[^>]+>)\b", text, re.I):
        errors.append("unresolved placeholder text is not allowed")
    limit = venue.get("limit_value")
    unit = venue.get("limit_unit")
    if isinstance(limit, int) and unit in {"chars", "words"}:
        if count_text(path, unit) > limit:
            errors.append(f"{label} exceeds the {unit} limit")
    return errors


def _draft_errors(case_dir: Path, state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    errors.extend(_venue_rules_errors(state))
    errors.extend(_issue_errors(state))
    if (state.get("approvals") or {}).get("strategy") != "approved":
        errors.append("strategy approval is required before drafting")
    if not (Path(case_dir) / "DRAFT.md").exists():
        errors.append("DRAFT.md is missing")

    evidence_by_id = {
        e.get("id"): e for e in state.get("evidence", []) if isinstance(e, dict)
    }
    allowed_statuses = {"paper_verified", "author_confirmed", "public_verified"}
    for issue in state.get("issues", []):
        if not isinstance(issue, dict):
            continue
        if issue.get("status") not in {"answered", "deferred", "needs_user_input"}:
            errors.append(f"{issue.get('id', '<unnamed issue>')} is not dispositioned")
        for evidence_id in issue.get("evidence_ids", []):
            evidence = evidence_by_id.get(evidence_id)
            if not evidence:
                errors.append(f"{issue.get('id', '<unnamed issue>')} references missing evidence {evidence_id}")
            elif evidence.get("status") not in allowed_statuses:
                errors.append(f"unverified evidence: {evidence_id}")

    draft_path = Path(case_dir) / "DRAFT.md"
    errors.extend(_text_errors(draft_path, state.get("venue") or {}, "DRAFT.md"))
    return errors


def validate_case(case_dir: Path, gate: str) -> list[str]:
    """Return blocking errors for a workflow gate; an empty list means pass."""

    state, errors = _load_state(Path(case_dir))
    if state is None:
        return errors
    if gate not in {"strategy", "draft", "paste-ready", "escalation"}:
        return [f"unknown gate: {gate}"]
    if gate == "strategy":
        errors.extend(_venue_rules_errors(state))
        errors.extend(_issue_errors(state))
        return errors
    errors.extend(_draft_errors(Path(case_dir), state))
    if gate == "draft":
        return errors
    approvals = state.get("approvals") or {}
    if gate == "paste-ready":
        if approvals.get("facts") != "approved":
            errors.append("fact approval is required before paste-ready output")
        if approvals.get("paste_ready") != "approved":
            errors.append("paste-ready approval is required")
        errors.extend(_text_errors(Path(case_dir) / "PASTE_READY.txt", state.get("venue") or {}, "PASTE_READY.txt"))
        return errors
    if approvals.get("escalation") not in {"mentor_approved", "approved"}:
        errors.append("mentor approval is required before escalation")
    return errors


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--case-dir", required=True, type=Path)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--case-dir", required=True, type=Path)
    check_parser.add_argument(
        "--gate", required=True, choices=["strategy", "draft", "paste-ready", "escalation"]
    )

    count_parser = subparsers.add_parser("count")
    count_parser.add_argument("--file", required=True, type=Path)
    count_parser.add_argument("--unit", choices=["chars", "words"], default="chars")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.command == "init":
        initialize_case(args.case_dir)
        print(f"initialized case workspace: {args.case_dir}")
        return 0
    if args.command == "count":
        print(count_text(args.file, args.unit))
        return 0
    errors = validate_case(args.case_dir, args.gate)
    if errors:
        for error in errors:
            print(f"BLOCKED: {error}")
        return 1
    print(f"PASS: {args.gate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
