# NeurIPS Rules and Workflow Overlay

Verify every rule against the current official cycle before drafting. This reference contains the verified NeurIPS 2026 baseline, not a permanent rule set.

## Official sources

| Source | Use |
| --- | --- |
| [Main Track Handbook](https://neurips.cc/Conferences/2026/MainTrackHandbook) | response mechanics, anonymity, links, new results, contact route, publication policy |
| [Dates and deadlines](https://neurips.cc/Conferences/2026/Dates) | current phase and deadlines |
| [Reviewer guidelines](https://neurips.cc/Conferences/2026/ReviewerGuidelines) | contribution-type interpretation and review criteria |
| [AC pilot announcement](https://blog.neurips.cc/2026/03/23/refining-the-review-cycle-neurips-2026-area-chair-pilot/) | initial meta-review purpose and critical-concern focus |

If a current official source conflicts with this reference, use the official source, record the difference in `RULES_SNAPSHOT.md`, and do not silently reuse the 2026 profile.

## Verified 2026 Main Track profile

```text
rules_profile_id: neurips-2026-main
response_mode: per_review_openreview
limit_scope: per_review
limit: 10000 characters
format: OpenReview plain text with Markdown
additional_files: forbidden
ordinary_links: forbidden
paper_or_supplement_revision_during_response: forbidden
new_results: allowed only as a response; submitted paper remains the decision basis
```

Authors use the Rebuttal button to respond to each review. Check the readers of every comment. Do not include identifying information. Do not use links in a response. If a reviewer asks for code, the handbook permits an anonymized link only in an Official Comment to the AC; verify that route and the current form before drafting it.

## Phase-aware plan

| 2026 phase | Author action | Stop rule |
| --- | --- | --- |
| Review release to initial-response close | Read reviews and initial meta-review; prepare every per-review response | Do not expect reviewer interaction before responses are released |
| Author, reviewer, AC discussion | Answer a new question, correction, or confirmed direct result once | Do not repost or pressure a reviewer about score |
| Reviewer, AC discussion | Authors cannot view continued discussion | No author follow-up |

Record exact local deadline, source URL, and timezone. The 2026 dates page lists review release on July 22, author-reviewer-AC discussion from July 27 to August 3, and reviewer-AC discussion from August 3 to August 10.

## Initial meta-review map

The initial meta-review may identify critical concerns, distinguish them from non-critical suggestions, and make the subsequent decision process more focused. Map every critical concern to one or more atomic issues and one or more response files. If a reviewer requests an experiment that the initial meta-review does not treat as decision-relevant, answer the bounded question but do not let it displace a critical concern.

## Contribution-type calibration

Main Track uses General, Theory, Use-Inspired, Concept & Feasibility, and Negative Results contribution types. Do not defend a theory paper as though a new large-scale benchmark were universally required, or a negative-result paper as though it must introduce a mitigation. State the selected type, the relevant Quality, Clarity, Significance, and Originality interpretation, and the precise claim boundary.

## New results and scope

Use `direct_response_new_result` only when all conditions hold:

1. It directly answers a reviewer or AC question.
2. It is complete and author-confirmed.
3. It clarifies or tests the submitted claim rather than replacing the paper.
4. The response states the matched setting and limitation.

Use `unconfirmed_new_result`, `major_scope_change`, or `unsolicited_new` when the condition fails. The checker blocks those origins. Never promise to revise the paper during the author-response period; record any later camera-ready possibility separately in `REVISION_PLAN.md`.

## AC communication

The assigned AC is the first venue contact for a paper. Use an OpenReview comment with correct readers and a narrow factual request. Use `AC_SUMMARY.md` before `AC_MESSAGE.md`; mentor approval is mandatory. Do not ask for acceptance or a score change. If escalation is necessary, describe timestamps, review anchors, factual effect, and the smallest requested handling.
