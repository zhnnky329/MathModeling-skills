---
name: related-paper-analyzer
description: Collect and analyze relevant papers, reports, and reference methods to inform method selection without fabricating references or copying models blindly.
license: MIT
---

# Purpose

Analyze user-provided papers and reports before final method selection.

This skill checks whether the user has placed original paper files under `workspace/papers/`, reads those originals, and extracts transferable method cues, assumptions, variables, validation ideas, and limitations for the current subquestions.

This skill does not fabricate references, browse for new papers, write the final method card, or copy a published model blindly.

# When to use

Use this skill:

- After `problem-parser` and `problem-classifier` have produced validated artifacts.
- Before `method-selector`.
- When the team wants to ground method selection in user-supplied literature rather than guessing from model names.
- When original papers, reports, or extracted paper text are available under `workspace/papers/`.

# Preconditions

The following should already exist or be provided:

- A validated problem parse.
- A validated problem classification artifact.
- At least one original paper file under `workspace/papers/`.

If no paper originals are present under `workspace/papers/`, stop and remind the user to place them there before analysis begins.

# Inputs

Use or request:

- `workspace/problem/problem-parser/problem_parse.json`, if available.
- `workspace/problem/problem-classifier/problem_classification.json`, if available.
- Original paper files under `workspace/papers/`.
- User notes about which papers matter most, if available.

# Workflow

1. Check `workspace/papers/` first.
   - Look for user-supplied paper originals or extracted paper text.
   - Accept formats such as `.pdf`, `.docx`, `.md`, `.txt`, or clearly named extracted text files.
   - Ignore `workspace/papers/related_paper_analysis.md` if it already exists.

2. Stop early if the paper folder is empty.
   - If no paper originals are found, tell the user to place the paper originals under `workspace/papers/`.
   - Do not fabricate literature summaries from memory.

3. Inventory the available papers.
   - Record file name, apparent title if recoverable, likely language, and likely relevance.
   - Mark unreadable or weakly relevant files explicitly.

4. Read papers for modeling signals.
   - Extract task type, assumptions, variables, data requirements, method families, outputs, validation patterns, and limitations.
   - Focus on transferable ideas rather than copying a complete published pipeline.

5. Map literature cues to the current problem.
   - Link relevant papers to specific subquestions such as `Q1`, `Q2`, or `Q3`.
   - Distinguish useful method cues from paper-specific tricks that should not be copied directly.

6. Summarize risks and reuse boundaries.
   - Flag assumptions that may not fit the current contest problem.
   - Flag data requirements that the current workspace may not satisfy.
   - Flag methods that look impressive in papers but may be infeasible under contest constraints.

7. Write the literature analysis report.
   - Save the report as `workspace/papers/related_paper_analysis.md`.
   - Keep it concise, traceable, and ready for `method-selector`.

8. Hand off to `method-selector`.
   - Pass forward the paper inventory, method cues, cautions, and unresolved evidence gaps.

# Outputs

Produce one Markdown literature-analysis artifact:

- `workspace/papers/related_paper_analysis.md`

The report should include:

- reviewed paper inventory
- per-paper summary
- subquestion-to-paper mapping
- transferable method cues
- assumptions or limitations worth carrying forward
- methods that should not be copied blindly
- missing evidence or unresolved questions
- recommended next skill

# Output format

Write a Markdown report at `workspace/papers/related_paper_analysis.md`.

Suggested sections:

- Reviewed papers
- Transferable method cues by subquestion
- Useful assumptions, variables, and validation ideas
- Risks of direct reuse
- Missing evidence
- Recommended next skill

# Rules

- Analyze only user-supplied papers or extracted paper text under `workspace/papers/`.
- Do not fabricate titles, authors, years, venues, DOIs, or conclusions.
- Do not browse for new literature inside this skill.
- Do not turn literature analysis into final method selection.
- Do not override the validated problem parse or classification.
- Do not copy a paper's model blindly without checking fit to the current subquestion, data, and contest constraints.
- Do not skip the initial check for paper originals in `workspace/papers/`.

# Verification

Before handoff, verify:

- `workspace/papers/` was checked for user-supplied paper originals.
- At least one paper file was found, or a clear blocker was reported.
- Each relevant subquestion has mapped paper cues or an explicit note that no relevant paper was found.
- Transferable ideas are separated from risky direct reuse.
- The report is saved at `workspace/papers/related_paper_analysis.md`.
- The next skill is `method-selector`.

# Failure modes

Stop and report a blocker if:

- `workspace/papers/` contains no paper originals.
- All paper files are unreadable or corrupted.
- The files are too incomplete to identify any reusable method cues.
- The user asks for method selection or paper claims before literature analysis is available.

# Stop conditions

This skill must stop instead of guessing when:

- No original papers are available under `workspace/papers/`.
- File contents are too incomplete to support a trustworthy summary.
- Continuing would require inventing references, assumptions, or paper conclusions.

When stopping, output:

- the blocker
- why it matters
- the checked folder path
- readable files found, if any
- missing paper files or missing readable text
- recommended next action

# Handoff

After producing `workspace/papers/related_paper_analysis.md`, hand off to:

`method-selector`

The handoff should include:

- report path
- reviewed paper list
- per-subquestion literature cues
- reusable method families
- risky assumptions or direct-copy risks
- validation or robustness ideas worth carrying forward
- unresolved evidence gaps

# Examples

## Example 1: Papers missing

Input state:

- Problem parse and classification exist.
- `workspace/papers/` contains no original paper files.

Output:

```markdown
Blocker: no user-supplied paper originals were found under `workspace/papers/`.

Why it matters: this skill is designed to analyze original paper artifacts, not fabricate literature notes from memory.

Recommended next action: place the relevant paper originals or extracted paper text under `workspace/papers/`, then run `related-paper-analyzer` again.
```

## Example 2: Papers available

Input state:

- Problem parse and classification exist.
- `workspace/papers/` contains several relevant PDF papers.

Output:

- `workspace/papers/related_paper_analysis.md`

The report summarizes:

- which papers are relevant to `Q1`, `Q2`, and `Q3`
- which method families appear reusable
- which assumptions look risky under current contest data constraints
- which validation ideas should be passed to `method-selector`
