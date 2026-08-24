---
name: reference-manager
description: Manage and verify references for mathematical modeling contest papers, generating BibTeX entries, checking citation completeness, and ensuring all references are traceable to actual sources.
license: MIT
---

# Purpose

Manage and verify references for mathematical modeling contest papers.

This skill checks that every cited reference corresponds to an actual source, verifies that citations are placed where evidence is needed, generates properly formatted BibTeX entries for all references, and ensures that the paper does not contain fabricated citations.

This skill does not search for new papers, write paper sections, select methods, or perform QA on modeling content.

# When to use

Use this skill:

- After `paper-section-writer` has drafted paper sections with citations.
- Before `quality-assurance-auditor`.
- When the user says: "check the references", "generate BibTeX", "verify citations", "build refs.bib", "check if all citations are real".
- When the paper has `\cite{...}` or bracketed reference markers that need verification.
- When the related-paper analysis produced paper references that need to be formatted.

# Preconditions

The following should already exist or be provided:

- Paper section drafts with citations (`\cite{...}` or [1], [2], etc.).
- Related paper analysis at `workspace/papers/related_paper_analysis.md` (if available).
- User-provided paper files under `workspace/papers/` (if available).

# Inputs

Use or request:

- `paper/sections/*.md` or `paper/sections/*.tex` — paper drafts with citations.
- `workspace/papers/related_paper_analysis.md` — literature analysis with paper metadata.
- Paper files under `workspace/papers/` (PDF, etc.) for metadata extraction.
- Any existing `.bib` file the user has prepared.
- User notes about which references are most important.

# Workflow

1. Inventory all citations in the paper.
   - Scan all paper sections for `\cite{...}` commands, `[N]` markers, or author-year citations.
   - Build a complete list of unique citation keys or reference numbers.
   - Note where each citation appears and what claim it supports.

2. Match citations to source information.
   - For each citation, try to find its source:
     - In `workspace/papers/related_paper_analysis.md` — if a paper was analyzed.
     - In user-provided paper files under `workspace/papers/`.
     - In user-provided BibTeX or reference lists.
   - Mark citations that cannot be matched as "unverified".

3. Verify citation appropriateness.
   - Check that citations support the claims they're attached to.
   - Flag citations that appear irrelevant to the claim.
   - Flag "decorative citations" — citations added for appearance without actually supporting a claim.
   - Flag missing citations — claims that probably need a reference but have none.

4. Generate or update BibTeX entries.
   - For each verified reference, produce a properly formatted BibTeX entry.
   - Entry types: `@article`, `@book`, `@inproceedings`, `@misc`, `@techreport`.
   - Required fields per type:
     - `@article`: author, title, journal, year, volume, number, pages, doi (if available).
     - `@book`: author/editor, title, publisher, year, edition (if applicable).
     - `@inproceedings`: author, title, booktitle, year, pages, doi (if available).
     - `@misc`: author, title, howpublished, year, note, url (if applicable).
   - Use consistent citation keys: `AuthorYear` or `AuthorYearKeyword`.

5. Detect potential fabrication.
   - A citation is flagged as potentially fabricated if:
     - No source file or metadata can be found.
     - The title, author, year, or venue cannot be verified from available sources.
     - The citation key exists but has no corresponding entry.
     - The paper metadata looks generic or ai-generated (placeholder titles, obviously fake DOIs).
   - Potentially fabricated citations are reported as blocking issues.

6. Produce or update `paper/refs.bib`.
   - Save all verified BibTeX entries to `paper/refs.bib`.
   - Ensure the file is valid BibTeX (balanced braces, proper field separators).
   - Mark unverified entries with `%% UNVERIFIED — needs author confirmation`.

7. Produce a reference audit report.
   - Save as `paper/reference_audit.md`.
   - Include: citation inventory, match status, fabrication flags, missing citation suggestions.

# Outputs

- `paper/refs.bib` — BibTeX file with all verified references.
- `paper/reference_audit.md` — Reference audit report.

# Output format

## `paper/refs.bib`

```bibtex
% ── Verified references ──────────────────────────────────────────────

@article{Wang2023TOPSIS,
  author    = {Wang, X. and Li, Y. and Zhang, H.},
  title     = {Entropy-weight TOPSIS method for multi-criteria urban resilience evaluation},
  journal   = {Journal of Urban Planning and Development},
  year      = {2023},
  volume    = {149},
  number    = {2},
  pages     = {04023001},
  doi       = {10.1061/JUPDD.0000123}
}

@book{Xu2018Modeling,
  author    = {Xu, Z.},
  title     = {Mathematical Modeling: Methods and Applications},
  publisher = {Higher Education Press},
  year      = {2018},
  edition   = {3rd}
}

@misc{COMAP2026,
  author    = {{COMAP}},
  title     = {MCM/ICM 2026 Problem A Statement},
  howpublished = {Contest problem statement},
  year      = {2026}
}

% ── UNVERIFIED — needs author confirmation ───────────────────────────

%% UNVERIFIED @article{Someone2024Method,
%%   author    = {Someone, A.},
%%   title     = {A Method for Something},
%%   journal   = {Unknown Journal},
%%   year      = {2024}
%% }
```

## `paper/reference_audit.md`

```markdown
# Reference Audit Report

> Last updated: [timestamp]

## 1. Citation Inventory

| # | Citation Key | Appears In | Claim Supported | Status |
|---|-------------|-----------|----------------|--------|
| 1 | `Wang2023TOPSIS` | Q1 Model Construction | "Entropy-TOPSIS is widely used..." | ✅ Verified |
| 2 | `Xu2018Modeling` | Assumptions | "Linear aggregation is common..." | ✅ Verified |
| 3 | `COMAP2026` | Problem Restatement | Problem source | ✅ Verified |
| 4 | `Someone2024Method` | Q3 Model Construction | "This method is optimal..." | ❌ UNVERIFIED |

## 2. Fabrication Risk Assessment

| Citation | Risk Level | Reason |
|----------|-----------|--------|
| `Someone2024Method` | HIGH | No source file found; author name "Someone" appears placeholder-like; no DOI or venue verifiable |

## 3. Missing Citation Suggestions

| Claim | Location | Suggested Citation |
|-------|----------|-------------------|
| "TOPSIS was first proposed by..." | Q1 Model Construction | Hwang & Yoon (1981) — Multiple Attribute Decision Making |

## 4. Recommendations

1. **BLOCKING**: Verify or remove `Someone2024Method` — appears to be fabricated.
2. **SUGGESTION**: Add Hwang & Yoon (1981) as the foundational TOPSIS reference.
3. **SUGGESTION**: Verify all DOIs resolve correctly before final submission.
```

# Citation Verification Rules

- Every `\cite{...}` in the paper must have a corresponding entry in `paper/refs.bib`.
- Every entry in `paper/refs.bib` must have at minimum: author, title, year.
- A citation without any verifiable source (file, metadata, or user confirmation) is flagged as potentially fabricated.
- Contest papers should cite: the problem statement, key methodology references, data sources (if external), and comparison baselines.
- Do not fabricate DOIs, page numbers, volume numbers, or author names.
- Do not add "impressive-looking" references that were not actually consulted.
- References should primarily support the methodology; avoid padding the reference list.

# Rules

- Do not fabricate references, metadata, or DOIs.
- Do not add references that were not used in the paper.
- Every citation must be traceable to an actual source.
- Flag unverifiable citations as blocking issues — do not silently remove them.
- Generate BibTeX entries only for verified sources.
- Use consistent citation key format.
- Mark unverified entries explicitly in the `.bib` file.
- Contest problem statements and official attachments should be cited.

# Verification

Before handing off, verify:

- Every `\cite{...}` in the paper has a BibTeX entry (verified or flagged).
- Every BibTeX entry has author, title, and year at minimum.
- Unverified citations are explicitly flagged.
- Potential fabrication risks are reported.
- Missing citation suggestions are provided.
- The BibTeX file is syntactically valid.

# Failure modes

Stop and report a blocker if:

- A citation in the paper has NO traceable source and appears fabricated.
- Multiple citations share the same key but have different metadata.
- The paper cites a source that contradicts the paper's own claims.
- A critical methodology claim has no supporting citation and no justification.

# Stop conditions

This skill must stop instead of guessing when:

- A citation's source cannot be found and the user cannot provide it.
- The BibTeX file would contain fabricated entries.
- A reference appears to be entirely made up.

When stopping, output:
- the problematic citation
- why it's flagged
- what the author needs to provide (real source, or remove the citation)

# Handoff

After producing `paper/refs.bib` and `paper/reference_audit.md`, hand off to:

`quality-assurance-auditor`
— which will include reference verification in the final QA check.

The handoff should include:
- `paper/refs.bib` path.
- `paper/reference_audit.md` path.
- List of unverified citations needing author attention.
- Fabrication risk flags.

# Examples

## Example 1: Clean audit

```markdown
## 1. Citation Inventory

| Citation Key | Status |
|-------------|--------|
| `Hwang1981TOPSIS` | ✅ Verified — from related_paper_analysis.md |
| `Wang2023Entropy` | ✅ Verified — from workspace/papers/wang2023.pdf |
| `COMAP2026` | ✅ Verified — contest problem statement |
| `Xu2018Modeling` | ✅ Verified — user-provided reference |
```

## Example 2: Fabrication detected

```markdown
## 2. Fabrication Risk Assessment

| Citation | Risk | Reason |
|----------|------|--------|
| `Smith2025BestMethod` | HIGH | No paper file found. No metadata in related_paper_analysis.md. Author "Smith" + generic title "Best Method for Evaluation" looks auto-generated. Google Scholar shows no match. |

**Recommendation**: Remove this citation or provide the actual paper. Do not submit the paper with this citation.
```
