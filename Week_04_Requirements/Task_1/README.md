# Requirements Refinement Agentic Network

This project implements an agentic network for software requirements refinement.

The program reads a directory with `.txt` and `.eml` files, extracts software requirements from them, refines the requirements, checks their quality, and generates one structured requirements document.

The solution is implemented in Python using LangGraph.

## Architecture

```text
load_documents
      |
      v
extract_requirements
      |
      v
refine_requirements
      |
      v
review_requirements
      |
   PASS / FAIL
      |
      +---- FAIL ----> refine_requirements
      |
      +---- PASS or maximum attempts ----> write_output
```

## Nodes

### 1. load_documents

This is a deterministic node.

It recursively reads all `.txt` and `.eml` files from the input directory.

The path to the input directory is provided when the program is started, so the solution does not use hard-coded input file names.

### 2. extract_requirements

Model: `gpt-5.6-luna`

This node processes every input document and extracts possible software requirements.

It also keeps:
- functional requirements,
- non-functional requirements,
- constraints,
- assumptions,
- dependencies,
- unclear requirements.

Each extracted candidate gets a unique ID such as `CAND-001`.

### 3. refine_requirements

Model: `gpt-6-luna`

This node creates the final requirements from the extracted candidates.

It:
- merges semantic duplicates,
- resolves or identifies conflicts,
- uses consistent terminology,
- assigns priorities,
- keeps source references,
- creates a blacklist for rejected or invalid requirements.

Because the input can contain many candidates, refinement is processed in smaller batches and then globally consolidated.

Final requirements receive IDs such as `REQ-001`.

Rejected requirements receive IDs such as `BL-001`.

### 4. review_requirements

Model: `gpt-5-mini`

This node checks the refined requirements.

It checks:
- completeness,
- semantic duplicates,
- contradictions,
- terminology,
- unique IDs,
- priorities,
- source tracing,
- blacklist quality,
- required names and descriptions.

If the result is `FAIL`, the reviewer sends corrections back to the refiner.

The workflow allows up to three review attempts.

### 5. write_output

This is a deterministic node.

It validates the final data and writes one structured Markdown document:

```text
output/requirements.md
```

## Retry and Review Limits

The reviewer can check the requirements up to three times.

If the reviewer returns `FAIL`, the result is sent back to the refiner for correction.

During refinement, if some candidate requirements are accidentally omitted, the refiner can make up to two recovery attempts for the missing candidates.

## Output Requirements

The workflow addresses all required output specifications:

| Spec | How it is addressed |
|---|---|
| OS1 | One structured Markdown requirements document is generated |
| OS2 | Every requirement receives a unique `REQ-*` ID |
| OS3 | The refiner merges semantic duplicates and the reviewer checks them |
| OS4 | Every requirement contains source document paths |
| OS5 | Every requirement has a short name and a paragraph description |
| OS6 | Every requirement has High, Medium, or Low priority and the scale is explained |
| OS7 | The refiner and reviewer check terminology and contradictions |
| OS8 | Every input document is processed and extracted candidates are checked for coverage |
| OS9 | Rejected requirements are stored in a separate blacklist with reasons |

## Agentic Network Requirements

The implementation satisfies the required network specifications:

| Spec | Implementation |
|---|---|
| ANS1 | Three LLM nodes: extractor, refiner, reviewer |
| ANS2 | Deterministic loader and output writer |
| ANS3 | Reviewer can send a failed result back to the refiner |
| ANS4 | Three models are used: `gpt-5.6-luna`, `gpt-6-luna`, `gpt-5-mini` |
| ANS5 | The workflow is implemented with Python LangGraph |

## API Key

The program uses `python-dotenv`.

Create a file named:

```text
.env
```

inside the `Task_1` directory.

Add the API key:

```env
OPENAI_API_KEY=your-api-key
```

The `.env` file must not be committed to Git.

The program loads the key from `.env` when it starts.

## Installation

Install the required packages:

```bash
python -m pip install -r requirements.txt
```

## Running

Run the program from the `Task_1` directory:

```bash
python requirements_refinement.py data/corpus
```

The generated requirements document will be saved to:

```text
output/requirements.md
```

## Cache

The program stores temporary cache files to avoid repeating expensive API calls during debugging.

These files are not part of the final assignment output.

The final required generated document is:

```text
output/requirements.md
```

## Submission Files

The main files for the assignment are:

```text
requirements_refinement.py
requirements.txt
README.md
output/requirements.md
```