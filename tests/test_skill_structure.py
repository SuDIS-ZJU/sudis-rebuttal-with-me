import json
import stat
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "skills" / "sudis-rebuttal-with-me"


class SkillStructureTests(unittest.TestCase):
    def test_skill_has_required_frontmatter_and_stays_under_500_lines(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 500)
        self.assertTrue(text.startswith("---\nname: sudis-rebuttal-with-me\n"))
        self.assertIn("description: Use when", text.split("---", 2)[1])

    def test_references_are_directly_reachable_from_skill(self):
        required = {
            "intake-and-venue-rules.md",
            "strategy-and-reviewer-modeling.md",
            "evidence-and-experiment-priorities.md",
            "drafting-safe-rebuttals.md",
            "openreview-markdown.md",
            "followup-and-escalation.md",
            "anonymized-case-patterns.md",
        }
        actual = {p.name for p in (SKILL / "references").glob("*.md")}
        self.assertTrue(required.issubset(actual))
        for path in (SKILL / "references").glob("*.md"):
            self.assertLessEqual(len(path.read_text(encoding="utf-8").splitlines()), 300)

    def test_evals_cover_at_least_ten_realistic_cases(self):
        data = json.loads((ROOT / "evals" / "evals.json").read_text())
        self.assertGreaterEqual(len(data["evals"]), 10)
        self.assertTrue(all(item["prompt"] and item["expected_output"] for item in data["evals"]))

    def test_strategy_has_explicit_positive_negative_lanes(self):
        text = (SKILL / "references" / "strategy-and-reviewer-modeling.md").read_text(encoding="utf-8")
        for lane in (
            "positive-champion",
            "positive-conditional",
            "mixed-swing",
            "negative-addressable",
            "negative-fundamental",
            "negative-procedural-risk",
            "unknown-insufficient",
        ):
            self.assertIn(f"`{lane}`", text)
        self.assertIn("Never optimize for the number of reviewers who change scores", text)

    def test_install_script_is_executable_and_raw_materials_are_not_tracked(self):
        mode = (ROOT / "scripts" / "install.sh").stat().st_mode
        self.assertTrue(mode & stat.S_IXUSR)
        tracked = subprocess.run(
            ["git", "ls-files"], check=True, capture_output=True, text=True
        ).stdout
        self.assertNotIn("successful samples/", tracked)
        self.assertNotIn("experiments blog/", tracked)


if __name__ == "__main__":
    unittest.main()
