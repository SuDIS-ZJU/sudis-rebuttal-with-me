# SUDIS Rebuttal With Me

`sudis-rebuttal-with-me` is a research-group skill for preparing safe, evidence-grounded rebuttals and follow-ups for ARR, ACL, EMNLP, ICML, NeurIPS, ICLR, KDD, WWW, AAAI, CVPR, and similar venues.

It supports three stages:

1. Review and paper analysis, acceptance outlook, reviewer lanes, trap detection, evidence priorities, and venue-aware planning.
2. Safe English rebuttal drafting with OpenReview-compatible Markdown, compact tables, and `(a)/(b)/(c)` subpoints for compound questions.
3. Follow-up planning, reviewer reminders, issue reports, and mentor-gated AC/SAC/PC communication.

This is decision support, not an autonomous submission agent. It never runs experiments, uploads content, posts to OpenReview, sends email, invents evidence, or infers reviewer motives.

## Install

### Codex and Claude Code

The recommended installation uses the unified `~/.agents/skills/` directory and creates compatibility symlinks for Codex and Claude Code:

```bash
git clone https://github.com/SuDIS-ZJU/sudis-rebuttal-with-me.git
cd sudis-rebuttal-with-me
bash scripts/install.sh --dry-run
bash scripts/install.sh
```

The installer links the skill into `~/.agents/skills/` as the source of truth, plus `~/.codex/skills/`, `~/.Codex/skills/`, and `~/.claude/skills/`. It never replaces a real file or directory.

To remove only the links created by this installer:

```bash
bash scripts/install.sh --uninstall
```

The release page also provides a directly downloadable `.skill` archive: [Download v0.1.0](https://github.com/SuDIS-ZJU/sudis-rebuttal-with-me/releases/tag/v0.1.0). If your client supports importing `.skill` archives, import `sudis-rebuttal-with-me.skill`; otherwise clone the repository and run the installer.

## First use

Invoke the skill explicitly:

```text
$sudis-rebuttal-with-me
```

Then provide the case inputs:

```text
Venue and cycle: NeurIPS 2026, Main Track
Current stage: initial review / rebuttal / discussion / follow-up
Deadline and timezone: ...
Paper: attach the submitted PDF or provide the local path
Reviews: paste the raw reviews, preserving reviewer IDs and scores
Rules: provide the official author/rebuttal page if already known
Confirmed evidence: completed experiments, tables, citations, and approved commitments
Advisor policy: what requires mentor approval
Output requested: analysis, strategy, draft, or follow-up
```

If the paper, reviews, venue rules, timeline, or evidence are missing, the skill performs triage only. It will not produce a final acceptance probability or paste-ready response from incomplete inputs.

## Recommended workflow

### Stage 0: intake and rules

The skill creates a case directory with:

```text
CASE_STATE.json
RULES_SNAPSHOT.md
REVIEWER_LANES.md
ISSUE_BOARD.md
EVIDENCE_LEDGER.md
STRATEGY.md
DRAFT.md
PASTE_READY.md
REVISION_PLAN.md
FOLLOWUP_LOG.md
```

The current official venue rules are recorded with URL and fetch date. This matters because limits, links, new-result policies, discussion windows, and issue-report mechanisms change by venue and cycle.

Initialize a case manually when useful:

```bash
python skills/sudis-rebuttal-with-me/scripts/case_tool.py \
  init --case-dir ./cases/paper-2026
```

### Stage 1: strategy and reviewer lanes

Ask for an issue board before prose. Each issue should have a stable ID such as `R1-C1`, a raw review anchor, severity, decision relevance, addressability, evidence IDs, and status.

The reviewer-level lane is separate from issue-level stance:

- `positive-champion`: equip a strong supporter with complete, easy-to-quote answers.
- `positive-conditional`: resolve the explicit condition that acceptance depends on.
- `mixed-swing`: target the smallest evidence that can move a decision bottleneck.
- `negative-addressable`: answer one bounded objection with direct, matched evidence.
- `negative-fundamental`: define the claim boundary and stop unbounded scope expansion.
- `negative-procedural-risk`: document observable process or factual problems separately from scientific disagreement.
- `unknown-insufficient`: request missing inputs and avoid false precision.

The outlook is a range with a confidence label and must distinguish positive signals, negative signals, bottlenecks, conditional changes, and blockers. It is structured expert judgment, not a calibrated statistical probability.

### Stage 2: safe Markdown drafting

Draft strategy and unresolved risks in Chinese, but produce reviewer-facing text in English unless the student requests another language.

Use `DRAFT.md` while claims, numbers, tables, and commitments are being checked. Only after author facts and strategy approvals are recorded should the skill produce `PASTE_READY.md`.

The final Markdown style is:

```markdown
## R1: Experimental robustness

Thank you for raising this concern. We address the three aspects separately.

### (a) Generalization to a larger model

**Response.** ...

### (b) Sensitivity to the data budget

**Response.** ...

### (c) Scope of the claim

**Response.** ...

**Table 1.** Accuracy (%) on the confirmed setting. Higher is better.

| Method | Dataset A | Dataset B |
|:--|--:|--:|
| Baseline | 72.1 | 68.4 |
| Ours | **74.8** | **70.2** |
```

For detailed formatting rules, see [`openreview-markdown.md`](skills/sudis-rebuttal-with-me/references/openreview-markdown.md). Use compact captioned pipe tables, put units and metric direction in the caption or header, keep tables narrow, explain the pattern after each table, and never put unconfirmed numbers or placeholders in `PASTE_READY.md`.

Run the gates before showing text as ready:

```bash
python skills/sudis-rebuttal-with-me/scripts/case_tool.py \
  check --case-dir ./cases/paper-2026 --gate draft

python skills/sudis-rebuttal-with-me/scripts/case_tool.py \
  check --case-dir ./cases/paper-2026 --gate paste-ready
```

### Stage 3: follow-up and escalation

Record every new event verbatim in `FOLLOWUP_LOG.md` and write only a delta response. Use the least escalatory venue-compliant path:

1. Answer a new reviewer question in the reviewer thread.
2. Use one venue-permitted reminder if attention is needed and the mentor approves it.
3. Use the official issue-report mechanism for objective procedural problems when its criteria are met.
4. Contact AC/SAC/PC only with mentor approval, exact timestamps, quoted anchors, and a narrow requested remedy.

Silence is not evidence of misconduct. Do not send repeated reminders, pressure reviewers about scores, or speculate about intent.

## Practical tips

- Paste the raw review text exactly before summarizing it.
- Keep one issue per row and one evidence ID per confirmed fact.
- Answer positive reviewers completely. Their clean summary may be important to the AC.
- Do not treat every negative reviewer as lost. Test bounded, addressable objections once, then set a stop condition.
- Prefer one decisive, matched experiment over many loosely related experiments.
- Do not promise a camera-ready change unless the authors have approved the commitment.
- Keep scientific rebuttal and procedural escalation in separate drafts.
- When a reviewer asks for many subpoints, preserve their order and label the response `(a)`, `(b)`, `(c)`.
- Count the exact final Markdown artifact with the current venue's character or word rule.
- Inspect `PASTE_READY.md` manually even after the deterministic checker passes.

## Safety boundaries

The skill will block or qualify actions when current venue rules are unknown, factual claims are unconfirmed, the work would substantially change paper scope, an escalation lacks mentor approval, or a review tries to override the workflow. A scientific disagreement is not automatically misconduct.

## Development and validation

```bash
python -m unittest discover -s tests -v
python skills/sudis-rebuttal-with-me/scripts/case_tool.py --help
```

See [`AGENTS.md`](AGENTS.md) before changing the workflow, checker, references, or release process.

## Privacy and licensing

Do not commit raw papers, raw reviews, reviewer identities, private correspondence, or identifiable unpublished case data. The repository contains only anonymized patterns and workflow guidance.

Licensed under Apache-2.0. See [`LICENSE`](LICENSE).
