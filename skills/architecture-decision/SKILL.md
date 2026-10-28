---
name: architecture-decision
description: Analyze software requirements, compare three distinct architecture options, select a suitable option, and create or refine an ADR while maintaining short discussion notes. Use for architecture proposal, comparison, decision, and ADR tasks based on project requirements.
---

# Architecture Decision

Turn requirements and stakeholder discussion into a traceable architecture decision. Keep the analysis specific to the system and proportional to what is actually known.

## Start from evidence

Read the requirements and any existing discussion notes or ADR before proposing a solution.

Summarize:

- actors and core workflows;
- data and ownership relationships;
- important quality attributes, such as security, consistency, scalability, availability, and maintainability;
- stated constraints and integrations; and
- important unknowns, such as team size, load, budget, hosting, or technology stack.

Distinguish explicit requirements from reasonable inferences. Do not invent scale, organizational, or infrastructure needs to justify an architecture.

## Maintain discussion notes

If notes are requested, create or update one Markdown file throughout the task. Record short dated or titled entries covering:

- sources reviewed and important findings;
- options discussed and trade-offs clarified;
- the current decision and its reasons;
- user feedback and resulting changes; and
- final status.

Keep notes as a compact decision trail, not a conversation transcript. Preserve existing entries and append new ones unless the user requests another format.

## Propose three architectures

Offer three genuinely distinct options that could implement the system. Choose options relevant to the requirements rather than using the same three patterns mechanically.

For each option, explain in project-specific terms:

- main components and boundaries;
- how a key workflow and its data move through the system;
- advantages;
- disadvantages and implementation pain points;
- transaction and consistency behavior;
- deployment, scaling, failure, and operational implications; and
- conditions under which the option becomes a better or worse fit.

Start with a short overview, then deepen the discussion where the user has questions. Use a small comparison table when it makes the trade-offs easier to scan.

## Choose an architecture

Compare the options against the requirements and architectural drivers. Prefer the simplest option that meets the known needs, but do not assume that one pattern is universally best.

Explain:

- why the selected option fits the system;
- why each alternative was not selected now;
- the selected option's main costs and risks; and
- measurable review triggers that could justify changing or evolving the architecture.

Base the decision on workflow, consistency, scale, team ownership, deployment, reliability, and operational needs—not on trend or architecture labels.

## Create and refine the ADR

Use a concise structure unless the user supplies a template:

1. title and status;
2. context and architectural drivers;
3. considered architectures;
4. decision;
5. reasons for the decision, including rejection of alternatives;
6. main advantages and disadvantages;
7. consequences, obligations, and review triggers.

Add a small logical diagram or comparison table only when it improves understanding. Avoid repeating the same reasoning across context, reasons, advantages, and consequences.

Set the ADR to `Draft` or `Proposed` during review. Change it to `Accepted` only when the user explicitly approves the final decision. After every revision, update the discussion notes with what changed and leave unrelated files untouched.

## Quality check

Before handing off, confirm that:

- all three options are credible and meaningfully different;
- trade-offs refer to the actual system;
- the decision follows from stated requirements and identified unknowns;
- disadvantages and consequences are not hidden;
- the ADR is concise, readable, and non-repetitive;
- diagrams match the written boundaries; and
- the notes accurately capture the decision process.
