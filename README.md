# SUDIS Rebuttal With Me

`sudis-rebuttal-with-me` is a research-group skill for preparing safe, evidence-grounded rebuttals and follow-ups for ARR, ACL, EMNLP, ICML, NeurIPS, ICLR, KDD, WWW, AAAI, CVPR, and similar venues. `sudis-arr-rebuttal-with-me` is the first incremental venue overlay, specialized for ACL Rolling Review.

Copyright © 2026 SuDIS, Huan Li, and contributors. See [NOTICE](NOTICE) and [LICENSE](LICENSE).

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

The installer links both the general skill and the ARR overlay into `~/.agents/skills/` as the source of truth, plus `~/.codex/skills/`, `~/.Codex/skills/`, and `~/.claude/skills/`. It never replaces a real file or directory.

To remove only the links created by this installer:

```bash
bash scripts/install.sh --uninstall
```

The release page provides directly downloadable packages: [Download v0.2.2](https://github.com/SuDIS-ZJU/sudis-rebuttal-with-me/releases/tag/v0.2.2). Import both `sudis-rebuttal-with-me.skill` and `sudis-arr-rebuttal-with-me.skill` when using the independent ARR entry. The ARR overlay depends on the general skill.

## Venue-specific skill family

The family has one general skill and small venue overlays. The general skill owns the shared evidence, reviewer-lane, Markdown, approval, and escalation workflow. A venue overlay adds only current rules and venue-specific tactics.

| Venue or platform | Status | Entry point | What the overlay will specialize |
| --- | --- | --- | --- |
| ACL Rolling Review (ARR), including ACL/EMNLP-style ARR workflows | Available | [`sudis-arr-rebuttal-with-me`](skills/sudis-arr-rebuttal-with-me/SKILL.md) | Text-only response, no external links, minor add-on boundary, discussion budget, review-issue reports, ARR resubmission and commitment |
| NeurIPS | Coming soon | `sudis-neurips-rebuttal-with-me` | Cycle-specific response limits, reviewer/AC discussion, confidential communication and NeurIPS escalation rules |
| ICML | Coming soon | `sudis-icml-rebuttal-with-me` | Per-review limits, AC comments, response format and current-cycle discussion rules |
| ICLR | Coming soon | `sudis-iclr-rebuttal-with-me` | Public discussion, revision behavior, response limits and chair-facing workflow |
| KDD | Coming soon | `sudis-kdd-rebuttal-with-me` | Per-review rebuttal structure, tables, discussion and KDD-specific escalation |
| WWW | Coming soon | `sudis-www-rebuttal-with-me` | WWW review response, reviewer discussion and current committee contact rules |
| CVPR | Coming soon | `sudis-cvpr-rebuttal-with-me` | CVPR response limits, formatting and reviewer/AC follow-up |

“Coming soon” entries are placeholders, not installable skills. Do not apply their names or assumed limits to a live case.

## How to use the skill family

### Choose the entry point

Use the general entry when the venue has no overlay yet, or when you need venue-agnostic analysis:

```text
$sudis-rebuttal-with-me
```

Use a venue overlay when it is marked Available. The overlay always depends on the general skill:

```text
$sudis-arr-rebuttal-with-me
```

If the overlay is unavailable, install both packages from the same release. Do not mix an old general skill with a newer overlay unless the release notes explicitly allow it.

### Start with the smallest input

For the first turn, provide only:

1. the submitted paper PDF;
2. the raw review comments copied from OpenReview;
3. the venue or platform name if known.

Tell the skill whether you already have a raw author response, confirmed new experiments, the official cycle rules, a deadline, or mentor instructions. It will read the paper and reviews first, then ask interactive follow-up questions only for missing facts that change the next action.

### Let the skill progress through gates

The normal sequence is:

1. `triage`: paper/review understanding and missing-input checklist;
2. `strategy`: atomic issue board, reviewer lanes, outlook, evidence queue and stop conditions;
3. `draft`: Chinese strategy plus English reviewer-facing draft;
4. `paste-ready`: confirmed Markdown, tables, facts and approvals;
5. `follow-up`: delta replies, AC summary, issue report or chair-facing message.

Do not ask for a paste-ready response in the first turn. It will be blocked until rules, evidence and approvals are sufficient.

### Keep venue overlays incremental

For a specialized case, use the general files for the case ledger and the overlay files for venue constraints. For ARR, the important additional artifacts are `ARR_THREAD_PLAN.md`, `ARR_ISSUE_REPORT.md`, `AC_SUMMARY.md` and `AC_MESSAGE.md`. The same pattern will be used for future NeurIPS, KDD, WWW, ICML, ICLR and CVPR overlays.

## First use

Invoke the skill explicitly:

```text
$sudis-rebuttal-with-me
```

For an ARR case, use the specialized incremental entry:

```text
$sudis-arr-rebuttal-with-me
```

The ARR entry first applies the general workflow, then adds current ARR rules, ARR issue-report handling, discussion-budget planning, and ARR-specific sample patterns. Future venue overlays will follow the same design.

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

For ARR, also provide the cycle email or OpenReview form if it specifies a response limit, the current response count per reviewer thread, and whether this is a resubmission.

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
ARR_THREAD_PLAN.md
ARR_ISSUE_REPORT.md
AC_SUMMARY.md
AC_MESSAGE.md
```

The current official venue rules are recorded with URL and fetch date. This matters because limits, links, new-result policies, discussion windows, and issue-report mechanisms change by venue and cycle.

For ARR, record `venue.profile = "arr"`. The overlay requires text-only mode, links disabled, direct minor add-ons only, and an explicit limit status. It does not guess a permanent ARR character limit when the current cycle does not state one.

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

### ARR-specific workflow tips

- Treat ARR as a review platform, not as the final accept/reject venue.
- Keep the first author response focused on factual corrections and the most decision-relevant issues.
- Track at most two useful author responses per reviewer thread as a planning budget. A second response must add new information.
- Use only direct minor add-on experiments. Do not include unsolicited new models or substantial post-submission work.
- Keep `ARR_ISSUE_REPORT.md` separate from the scientific response and use the official issue type when applicable.
- After the meta-review, compare commitment, revise-and-resubmit, same-reviewer, new-reviewer, and direct-submission options separately.

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

Licensed under Apache-2.0. See [`LICENSE`](LICENSE). Third-party ARR rules and public advice remain the property of their respective authors and organizations; this repository distributes only original summaries and links.
