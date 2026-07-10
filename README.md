# SUDIS Rebuttal With Me

`sudis-rebuttal-with-me` is a research-group skill for planning, drafting, and following up on rebuttals for ARR, ACL, EMNLP, ICML, NeurIPS, ICLR, KDD, WWW, AAAI, CVPR, and similar venues.

It is decision support, not an autonomous submission agent. It never runs experiments, uploads content, sends messages, or invents evidence. It requires author confirmation for factual claims and mentor approval for escalation.

## Install locally

```bash
git clone <repository-url>
cd sudis-rebuttal
bash scripts/install.sh
```

The installer links the skill into `~/.agents/skills/` and creates compatibility symlinks for Codex and Claude Code. Use `bash scripts/install.sh --dry-run` to inspect paths first. The installer refuses to replace a real directory or file.

## Use

Invoke `$sudis-rebuttal-with-me` and provide the paper source, raw reviews, venue/cycle, deadline, and confirmed evidence. The skill creates a structured case workspace with a rules snapshot, issue board, evidence ledger, strategy, draft, revision plan, and follow-up log.

If the venue rules are missing or stale, the skill performs triage only. Always inspect `PASTE_READY.txt` and the approval records before submitting anything.

## Validate

```bash
python3 -m unittest discover -s tests -v
python3 skills/sudis-rebuttal-with-me/scripts/case_tool.py --help
```

The supplied OpenReview examples are research inputs used to create anonymized patterns. They are intentionally not distributed in this package.

## License

Apache-2.0. See [LICENSE](LICENSE).
