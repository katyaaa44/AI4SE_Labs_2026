# Task 3 Comparison Report

## Introduction

In Task 1 and Task 2 I worked with the RentYourExpert project without a reusable skill.

I first discussed different architecture options with the coding assistant and then created and improved an Architecture Decision Record. After that, I created the `architecture-decision` skill based on the notes from Task 1 and Task 2. Then I started a new session and repeated the same architecture analysis and ADR creation with the skill.

The skill is stored in the repository at `skills/architecture-decision/SKILL.md`.

## Without the skill

Without the skill, the work required many separate prompts.

In Task 1 I had to ask the assistant step by step to:
- read the requirements,
- propose three different architectures,
- explain each architecture,
- discuss advantages and disadvantages,
- explain implementation problems,
- compare the architectures,
- choose the best architecture.

In Task 2 I also needed several prompts to:
- create the first ADR,
- review it,
- shorten repeated parts,
- add a comparison table,
- add a simple architecture diagram,
- make the final version.

The result was good, but the process was longer because I had to explain the workflow many times.

## With the skill

After creating the `architecture-decision` skill, I started a new session. I only needed a short prompt to tell the assistant to use the skill.

The assistant already knew the main workflow:
- inspect the requirements,
- identify important architecture requirements,
- propose three architecture options,
- compare their trade-offs,
- choose the best option,
- create an ADR,
- keep short discussion notes.

Because of this, the architecture analysis and ADR were created much faster.

The result already included:
- three architecture alternatives,
- advantages and disadvantages,
- a comparison table,
- the selected architecture,
- an ADR structure,
- a simple logical diagram,
- discussion notes.

## Comparison

| Without skill | With skill |
|---|---|
| Many separate prompts | One main prompt plus only small follow-up changes |
| Workflow had to be explained manually | Workflow was already stored in the skill |
| More repeated instructions | Less repeated instructions |
| Architecture comparison was built step by step | Architecture comparison was created automatically |
| ADR needed several manual improvements | ADR was more complete from the beginning |
| Notes had to be requested separately | Notes were created as part of the workflow |
| Process was slower | Process was faster |
| More manual control was needed | The process was more consistent |

## Quality of the result

The final architecture decision was similar in both cases. In both runs, the layered modular monolith was selected as the best initial architecture for RentYourExpert.

Without the skill, the ADR was shorter and simpler. It was improved step by step after several reviews.

With the skill, the ADR was created faster and was more detailed from the beginning. It included more information about the three architectures, their advantages and disadvantages, operational aspects, risks, obligations, and review triggers. The skill-based ADR was more structured and more complete, but in some places it was also more detailed and professional than necessary for this task.

## Conclusion

The skill helped me complete Task 1 and Task 2 faster and with fewer prompts. It also reduced repeated explanations and made the workflow more consistent. The final result was similar to the original work, but I needed less manual guidance.