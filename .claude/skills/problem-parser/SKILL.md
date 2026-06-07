---
name: problem-parser
description: Parse a mathematical modeling problem into goals, objects, constraints, data, outputs, and subquestions.
license: MIT
---

# Purpose

Convert a raw mathematical modeling contest problem into a structured task specification.

This skill focuses on reading and decomposing the problem. It extracts what the contest is asking for, what objects are being studied, what data and constraints are available, what outputs are required, and how the subquestions depend on each other.

This skill does not classify the final problem type, select models, write code, or draft paper sections.

# When to use

Use this skill:

- After a new contest problem statement is provided.
- When problem text, PDF content, Word content, screenshots, or attachment descriptions need to be converted into a structured task brief.
- Before problem classification, method selection, code generation, or paper writing.
- When the team disagrees about what the problem is asking.
- When the current workflow lacks a validated problem parse artifact.

# Preconditions

At least one of the following must be available:

- The full problem statement.
- A readable excerpt of the problem statement.
- Screenshots or OCR text of the problem.
- A summary of the problem written by the user.
- Attachment descriptions or data file names.

If the problem statement is incomplete, parse the available content and mark the missing parts explicitly.

# Inputs

Use or request the following:

- Problem statement text or file location.
- Attachment descriptions, file names, and known data fields.
- Contest rules if they affect data usage, submission format, or allowed assumptions.
- User-provided notes about the team, contest deadline, or expected output.
- Existing `workspace/problem/` files, if available.

# Workflow

1. Read the problem for structure, not for model names.
   - Identify the real-world background.
   - Identify the main task and each subquestion.
   - Avoid jumping directly to algorithms.

2. Extract the five required reading labels.
   - goal: what should be achieved or explained
   - object: what entity, system, population, product, region, route, process, or decision is being studied
   - constraints: explicit and implicit limits
   - data: provided data, missing data, possible data sources, units, and data risks
   - output: required rankings, predictions, decisions, plans, figures, tables, explanations, or recommendations

3. Decompose every subquestion.
   - Assign each subquestion an ID such as `Q1`, `Q2`, `Q3`.
   - For each subquestion, extract input, processing need, expected output, constraints, and dependencies (these are mechanical — AI-owned).
   - Do NOT author the `evaluation_criteria` / success-definition. The rubric a judge grades against — what counts as a good answer — is a modeling judgment, not a parse. Emit it as a `[MODELER INPUT NEEDED: in the team's words, what makes an answer to this subquestion good?]` placeholder for the human to fill. The AI must not invent the rubric.
   - Mark whether a subquestion depends on the result of an earlier subquestion.

4. Extract variables, parameters, and relationships at a preliminary level.
   - List observable quantities.
   - List controllable quantities if the task appears decision-oriented.
   - List external parameters if they are given or must be estimated.
   - List obvious relationships, rules, conservation constraints, trends, or causal hints — but a mechanism claim (causal link, conservation law) is a modeling judgment, not a parse. Wrap each proposed relationship as `[AI-DRAFT — modeler must confirm: <relationship>]` so the human ratifies or rewrites it before it is treated as settled.
   - Do not finalize mathematical notation yet.

5. Identify ambiguity and risk.
   - Mark vague wording.
   - Mark missing data.
   - Mark unit inconsistencies.
   - Mark hidden assumptions.
   - Mark possible contest-rule risks such as external data dependence.

6. Produce a structured parse artifact.
   - Keep the artifact concise.
   - Preserve uncertainty instead of smoothing it over.
   - Save or recommend saving the paired outputs under `workspace/problem/problem-parser/`.

# Outputs

Produce a structured problem parse as paired artifacts:

- `workspace/problem/problem-parser/problem_parse.json`
- `workspace/problem/problem-parser/problem_parse.md`

The artifacts should contain:

- `background`
- `main_goal`
- `objects`
- `subquestions`
- `constraints`
- `data_inventory`
- `required_outputs`
- `preliminary_variables`
- `preliminary_relationships`
- `dependencies`
- `ambiguities`
- `risk_flags`
- `missing_information`
- `recommended_next_skill`

# Output format

Prefer this JSON-compatible structure for `workspace/problem/problem-parser/problem_parse.json`:

```json
{
  "background": "Short description of the real-world context.",
  "main_goal": "What the team must ultimately solve or explain.",
  "objects": [
    {
      "name": "object name",
      "scope": "time, location, population, system, or boundary if known"
    }
  ],
  "subquestions": [
    {
      "id": "Q1",
      "task": "What this subquestion asks for.",
      "input": [
        "Available or required input."
      ],
      "processing_need": [
        "What must be transformed, estimated, compared, optimized, explained, or validated."
      ],
      "output": [
        "Required deliverable for this subquestion."
      ],
      "constraints": [
        "Explicit or implicit limits."
      ],
      "depends_on": [],
      "evaluation_criteria": [
        "[MODELER INPUT NEEDED: in the team's words, what makes an answer to this subquestion good?]"
      ]
    }
  ],
  "constraints": {
    "explicit": [
      "Constraints directly stated in the problem."
    ],
    "implicit": [
      "Realistic constraints inferred from the context."
    ]
  },
  "data_inventory": {
    "provided": [
      {
        "name": "attachment or field name",
        "description": "Known content or role.",
        "unit": "unit if known",
        "risk": "missing, inconsistent, small sample, unclear definition, or none"
      }
    ],
    "missing": [
      "Data needed but not provided."
    ],
    "external_data_needed": false
  },
  "required_outputs": [
    "ranking, prediction, decision plan, parameter estimate, figure, table, explanation, or recommendation"
  ],
  "preliminary_variables": {
    "observable_quantities": [],
    "controllable_quantities": [],
    "external_parameters": [],
    "unknowns_to_estimate": []
  },
  "preliminary_relationships": [
    "[AI-DRAFT — modeler must confirm: qualitative or explicit relationship found in the problem.]"
  ],
  "dependencies": [
    {
      "from": "Q1",
      "to": "Q2",
      "reason": "Q2 uses the result of Q1."
    }
  ],
  "ambiguities": [
    "Ambiguous wording or unresolved interpretation."
  ],
  "risk_flags": [
    "Potential issue that may affect modeling."
  ],
  "missing_information": [
    "Information required to complete parsing or proceed safely."
  ],
  "recommended_next_skill": "problem-classifier"
}
```

Also produce `workspace/problem/problem-parser/problem_parse.md` with the same fields in readable Markdown form.

# Rules

- Do not select the final model.
- Do not recommend specific algorithms except as tentative reading cues, and only when clearly marked as tentative.
- Do not write code.
- Do not write paper sections.
- Do not fabricate missing problem details.
- Do not silently resolve ambiguity.
- Do not ignore units, data fields, output forms, or hidden constraints.
- Do not merge multiple subquestions into one vague task.
- Preserve the wording and intent of the original problem as much as possible.
- Mark uncertainty explicitly.
- Do not author the `evaluation_criteria` / success-definition. The rubric a judge grades against is the modeler's, not the parser's — emit it as `[MODELER INPUT NEEDED: in the team's words, what makes an answer to this subquestion good?]` and leave it for the human. The AI provides no draft to copy here.
- Do not finalize any `preliminary_relationships` (causal links, conservation laws, mechanism claims) on the human's behalf. Draft each one wrapped as `[AI-DRAFT — modeler must confirm: <relationship>]` so the human ratifies or rewrites it.
- A surviving `[AI-DRAFT` or `[MODELER INPUT NEEDED` sentinel in a finalized parse artifact is a GATE FAIL — exactly like a `<<<HUMAN>>>` sentinel in a decision artifact. The artifact is not "ready" until the human has replaced every such span. Do not strip a sentinel yourself to make the gate pass.

# Verification

Before handing off, verify:

- Every subquestion in the problem statement is represented.
- Each subquestion has input, processing need, output, and constraints.
- The five reading labels are covered: goal, object, constraints, data, output.
- Data availability and missing data are separated.
- Explicit constraints and implicit constraints are separated.
- Dependencies between subquestions are identified.
- Ambiguities and risk flags are listed instead of being hidden.
- No model has been selected prematurely.
- Each subquestion's `evaluation_criteria` carries a `[MODELER INPUT NEEDED: ...]` placeholder until the human supplies the rubric; the AI has authored none of it.
- Every `preliminary_relationships` entry is wrapped as `[AI-DRAFT — modeler must confirm: ...]` and none has been finalized as settled fact.
- The artifact is handed off as a DRAFT while any `[AI-DRAFT` or `[MODELER INPUT NEEDED` sentinel survives. A surviving sentinel is a GATE FAIL (treated like `<<<HUMAN>>>` in decision artifacts); the parse is "ready" only after the human has replaced every such span. Never strip a sentinel to force the gate.
- The next skill is `problem-classifier`.

# Failure modes

Stop and report a blocker if:

- The problem statement is unreadable or missing.
- A required attachment is referenced but not available, and parsing depends on it.
- The subquestions cannot be identified from the available content.
- The wording allows multiple materially different interpretations that would change the workflow.
- The user asks for model selection, code, or paper writing before parsing is complete.

# Stop conditions

This skill must stop instead of guessing when:

- The missing information changes the meaning of the task.
- A data file is essential to identify the required output.
- The problem statement is too incomplete to extract subquestions.
- Continuing would require inventing contest requirements, data fields, or numerical values.

When stopping, output:

- the blocker
- why it matters
- the exact missing information needed
- the part of the problem that can still be parsed
- the recommended next action after the blocker is resolved

# Handoff

After producing a validated problem parse, hand off to:

`problem-classifier`

The handoff should include:

- parsed subquestions
- goals, objects, constraints, data, and outputs
- preliminary variables and relationships
- ambiguity list
- risk flags
- missing information list

Do not hand off to `method-selector` directly unless `problem-classifier` has already been completed and validated.

# Examples

## Example 1: Basic parse

Input state:

- The problem asks the team to evaluate several cities, predict future demand, and propose an allocation plan.
- Attachments include historical indicators and demand data.

Output:

```json
{
  "main_goal": "Build a decision-support solution for city evaluation, demand prediction, and resource allocation.",
  "subquestions": [
    {
      "id": "Q1",
      "task": "Evaluate and rank cities.",
      "input": [
        "historical indicator data"
      ],
      "processing_need": [
        "construct evaluation criteria and produce comparable scores"
      ],
      "output": [
        "city ranking",
        "evaluation explanation"
      ],
      "constraints": [],
      "depends_on": [],
      "evaluation_criteria": [
        "[MODELER INPUT NEEDED: in the team's words, what makes an answer to this subquestion good?]"
      ]
    },
    {
      "id": "Q2",
      "task": "Predict future demand.",
      "input": [
        "historical demand data",
        "Q1 evaluation results if relevant"
      ],
      "processing_need": [
        "estimate future values and explain uncertainty"
      ],
      "output": [
        "future demand predictions",
        "error or uncertainty discussion"
      ],
      "constraints": [],
      "depends_on": [
        "Q1"
      ],
      "evaluation_criteria": [
        "[MODELER INPUT NEEDED: in the team's words, what makes an answer to this subquestion good?]"
      ]
    },
    {
      "id": "Q3",
      "task": "Propose an allocation plan.",
      "input": [
        "predicted demand",
        "resource limits"
      ],
      "processing_need": [
        "choose an allocation under constraints"
      ],
      "output": [
        "allocation decision",
        "implementation explanation"
      ],
      "constraints": [
        "limited resources"
      ],
      "depends_on": [
        "Q2"
      ],
      "evaluation_criteria": [
        "[MODELER INPUT NEEDED: in the team's words, what makes an answer to this subquestion good?]"
      ]
    }
  ],
  "recommended_next_skill": "problem-classifier"
}
```

## Example 2: Missing attachment

Input state:

- The problem says “use Attachment 1 to calculate the indicators.”
- Attachment 1 is not available.

Output:

```json
{
  "blocked_items": [
    "Attachment 1 is required to identify available indicators."
  ],
  "partial_parse_available": true,
  "missing_information": [
    "Attachment 1 or its field description"
  ],
  "recommended_next_action": "Provide the missing attachment or a list of its columns before classification."
}
```

## Example 3: Avoid premature modeling

Input state:

- User asks: “Can we use TOPSIS for this?”

Output:

```json
{
  "current_stage": "problem_parsing",
  "blocked_items": [
    "Model choice is premature before subquestions, data, and required outputs are parsed."
  ],
  "next_skill": "problem-parser",
  "next_actions": [
    "Extract goals, objects, constraints, data, outputs, and subquestions first.",
    "Then classify the subquestions before selecting methods."
  ]
}
```
