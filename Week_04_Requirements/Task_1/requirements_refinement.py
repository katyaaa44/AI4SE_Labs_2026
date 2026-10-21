from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Literal, TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_OUTPUT_PATH = BASE_DIR / "output" / "requirements.md"
EXTRACTION_CACHE_PATH = BASE_DIR / "output" / "extracted_candidates.json"
SUPPORTED_EXTENSIONS = {".txt", ".eml"}
MAX_REVIEW_ATTEMPTS = 3
REFINEMENT_BATCH_SIZE = 60
MAX_CONSOLIDATION_CHARS = 180_000
REFINEMENT_RECOVERY_ATTEMPTS = 2
REFINEMENT_CACHE_DIR = BASE_DIR / "output" / "refinement_batches"
REFINEMENT_PROMPT_VERSION = "v2"

PRIORITY_EXPLANATIONS = {
    "High": "Essential for core system operation or explicitly required by major stakeholders.",
    "Medium": "Important functionality but not essential for the first usable version.",
    "Low": "Optional, convenience, enhancement, or lower-impact functionality.",
}


# -----------------------------------------------------------------------------
# Structured data
# -----------------------------------------------------------------------------

class SourceDocument(BaseModel):
    source_path: str
    file_name: str
    file_type: str
    content: str


class ExtractedCandidate(BaseModel):
    statement: str = Field(description="One candidate software requirement")
    kind: Literal["functional", "non-functional", "constraint", "assumption", "dependency"]
    clarity: Literal["clear", "unclear"]
    evidence: str = Field(description="Short supporting excerpt or close paraphrase from the document")


class ExtractionResult(BaseModel):
    candidates: list[ExtractedCandidate]


class CandidateRequirement(BaseModel):
    candidate_id: str
    statement: str
    kind: str
    clarity: str
    source_path: str
    evidence: str


class RequirementDraft(BaseModel):
    name: str = Field(description="Short descriptive name")
    description: str = Field(description="A complete paragraph describing the requirement")
    priority: Literal["High", "Medium", "Low"]
    candidate_ids: list[str] = Field(description="All supporting candidate IDs")


class BlacklistDraft(BaseModel):
    name: str = Field(description="Short descriptive name")
    original_requirement: str = Field(description="Original requirement or concise summary")
    reason: str = Field(description="Specific reason for rejection")
    candidate_ids: list[str] = Field(description="All related candidate IDs")


class RefinementResult(BaseModel):
    requirements: list[RequirementDraft]
    blacklist: list[BlacklistDraft]


class Requirement(BaseModel):
    id: str
    name: str
    description: str
    priority: Literal["High", "Medium", "Low"]
    candidate_ids: list[str]
    sources: list[str]


class BlacklistItem(BaseModel):
    id: str
    name: str
    original_requirement: str
    sources: list[str]
    reason: str
    candidate_ids: list[str]


class ReviewCheck(BaseModel):
    category: Literal[
        "completeness",
        "duplicates",
        "contradictions",
        "terminology",
        "unique_ids",
        "priorities",
        "traceability",
        "blacklist",
        "required_fields",
    ]
    passed: bool
    details: str


class ReviewResult(BaseModel):
    verdict: Literal["PASS", "FAIL"]
    checks: list[ReviewCheck]
    corrections: list[str] = Field(
        description="Concrete, actionable corrections identifying missing or problematic items"
    )


class WorkflowState(TypedDict):
    input_dir: str
    output_path: str
    documents: list[SourceDocument]
    candidates: list[CandidateRequirement]
    requirements: list[Requirement]
    blacklist: list[BlacklistItem]
    review: ReviewResult | None
    review_feedback: list[str]
    review_attempts: int
    final_markdown: str
    refresh_extraction: bool


# -----------------------------------------------------------------------------
# Logging helpers
# -----------------------------------------------------------------------------

def log(message: str) -> None:
    """Print visible progress immediately."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)


def _safe_error_text(exc: Exception) -> str:
    """Return an exception message with API-key-like strings redacted."""
    text = str(exc)
    text = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "sk-***REDACTED***", text)
    return text


# -----------------------------------------------------------------------------
# Deterministic document loading
# -----------------------------------------------------------------------------

def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _read_email(path: Path) -> str:
    with path.open("rb") as handle:
        message = BytesParser(policy=policy.default).parse(handle)

    headers = [
        f"{name}: {message.get(name, '')}"
        for name in ("From", "To", "Subject", "Date")
        if message.get(name)
    ]
    body = message.get_body(preferencelist=("plain",)) if message.is_multipart() else message
    if body is None:
        body_text = ""
    else:
        try:
            body_text = body.get_content()
        except (AttributeError, KeyError, LookupError):
            payload = body.get_payload(decode=True)
            body_text = payload.decode("utf-8", errors="replace") if payload else ""
    return "\n".join(headers + ["", body_text]).strip()


def load_documents(state: WorkflowState) -> dict[str, object]:
    input_dir = Path(state["input_dir"]).expanduser().resolve()
    log(f"Stage 1/5: loading documents from {input_dir}")

    if not input_dir.exists():
        raise FileNotFoundError(f"Corpus directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Corpus path is not a directory: {input_dir}")

    paths = sorted(
        path
        for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )
    if not paths:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"No supported documents ({supported}) found in {input_dir}")

    documents: list[SourceDocument] = []
    for index, path in enumerate(paths, start=1):
        rel = path.relative_to(input_dir).as_posix()
        log(f"  loading {index:02d}/{len(paths):02d}: {rel}")
        content = _read_email(path) if path.suffix.lower() == ".eml" else _read_text(path)
        if not content.strip():
            log(f"  skipped empty document: {rel}")
            continue
        documents.append(
            SourceDocument(
                source_path=rel,
                file_name=path.name,
                file_type=path.suffix.lower(),
                content=content,
            )
        )

    if not documents:
        raise ValueError(f"All supported documents in {input_dir} were empty")

    log(f"Loaded {len(documents)} supported documents")
    return {"documents": documents}


# -----------------------------------------------------------------------------
# Extraction cache
# -----------------------------------------------------------------------------

def _corpus_fingerprint(documents: list[SourceDocument]) -> str:
    digest = hashlib.sha256()
    for document in sorted(documents, key=lambda item: item.source_path):
        digest.update(document.source_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(document.content.encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _load_extraction_cache(
    documents: list[SourceDocument], refresh: bool
) -> list[CandidateRequirement] | None:
    if refresh or not EXTRACTION_CACHE_PATH.exists():
        return None

    try:
        payload = json.loads(EXTRACTION_CACHE_PATH.read_text(encoding="utf-8"))
        if payload.get("corpus_fingerprint") != _corpus_fingerprint(documents):
            log("Extraction cache exists but corpus changed; cache will be ignored")
            return None
        raw_candidates = payload.get("candidates", [])
        candidates = [CandidateRequirement.model_validate(item) for item in raw_candidates]
        if not candidates:
            return None
        return candidates
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        log(f"Extraction cache is invalid and will be ignored: {_safe_error_text(exc)}")
        return None


def _save_extraction_cache(
    documents: list[SourceDocument], candidates: list[CandidateRequirement]
) -> None:
    EXTRACTION_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "corpus_fingerprint": _corpus_fingerprint(documents),
        "candidate_count": len(candidates),
        "candidates": [candidate.model_dump() for candidate in candidates],
    }
    EXTRACTION_CACHE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log(f"Saved extraction cache to {EXTRACTION_CACHE_PATH}")


# -----------------------------------------------------------------------------
# LLM node 1: extraction
# -----------------------------------------------------------------------------

def extract_requirements(state: WorkflowState) -> dict[str, object]:
    log("Stage 2/5: extracting candidate requirements")

    cached = _load_extraction_cache(
        state["documents"], state.get("refresh_extraction", False)
    )
    if cached is not None:
        log(f"Cache hit: loaded {len(cached)} candidate requirements; no extraction API calls needed")
        return {"candidates": cached}

    log("Cache miss: starting OpenAI extraction calls")

    # Do not pass temperature; some newer models reject unsupported sampling parameters.
    model = ChatOpenAI(model="gpt-5.6-luna")
    extractor = model.with_structured_output(ExtractionResult, method="json_schema")

    system_prompt = """You are a meticulous software requirement extractor.
Extract every candidate requirement, constraint, assumption, and dependency in the supplied document.
Keep distinct requirements separate, but do not create duplicates merely because a point is repeated.
Ignore personal chatter and meeting administration that do not describe the software.
Never silently discard an unclear, tentative, or underspecified software request: include it with clarity
set to 'unclear'. Preserve a short supporting excerpt or close paraphrase as evidence. Do not invent IDs.
Return only data matching the supplied schema."""

    candidates: list[CandidateRequirement] = []
    total = len(state["documents"])
    for doc_index, document in enumerate(state["documents"], start=1):
        log(f"  [extract {doc_index:02d}/{total:02d}] {document.source_path} ...")
        result = extractor.invoke(
            [
                ("system", system_prompt),
                (
                    "human",
                    f"Source path: {document.source_path}\n\nDocument:\n{document.content}",
                ),
            ]
        )
        if not isinstance(result, ExtractionResult):
            result = ExtractionResult.model_validate(result)

        for extracted in result.candidates:
            candidates.append(
                CandidateRequirement(
                    candidate_id="",
                    statement=extracted.statement.strip(),
                    kind=extracted.kind,
                    clarity=extracted.clarity,
                    source_path=document.source_path,
                    evidence=extracted.evidence.strip(),
                )
            )
        log(
            f"  [extract {doc_index:02d}/{total:02d}] done: "
            f"{len(result.candidates)} candidates from this document; {len(candidates)} total"
        )

    candidates.sort(
        key=lambda candidate: (
            candidate.source_path.casefold(),
            candidate.statement.casefold(),
            candidate.evidence.casefold(),
        )
    )
    for index, candidate in enumerate(candidates, start=1):
        candidate.candidate_id = f"CAND-{index:03d}"

    log(f"Extraction complete: {len(candidates)} candidate requirements")
    _save_extraction_cache(state["documents"], candidates)
    return {"candidates": candidates}


# -----------------------------------------------------------------------------
# Refinement helpers
# -----------------------------------------------------------------------------

def _candidate_lookup(state: WorkflowState) -> dict[str, CandidateRequirement]:
    return {candidate.candidate_id: candidate for candidate in state["candidates"]}


def _valid_candidate_ids(
    ids: list[str], lookup: dict[str, CandidateRequirement]
) -> list[str]:
    return sorted(set(candidate_id for candidate_id in ids if candidate_id in lookup))


def _sources_for(
    ids: list[str], lookup: dict[str, CandidateRequirement]
) -> list[str]:
    return sorted({lookup[candidate_id].source_path for candidate_id in ids})


def _candidate_sort_key(ids: list[str]) -> tuple[int, ...]:
    numbers = []
    for candidate_id in ids:
        try:
            numbers.append(int(candidate_id.rsplit("-", 1)[1]))
        except (IndexError, ValueError):
            continue
    return tuple(sorted(numbers)) or (sys.maxsize,)


def _chunks(items: list, size: int):
    for start in range(0, len(items), size):
        yield items[start : start + size]


def _refinement_system_prompt() -> str:
    return f"""You are a senior software requirements analyst. Produce a coherent specification
from the supplied candidate requirements or draft requirements. Merge semantic duplicates and preserve the
union of every supporting candidate_id. Use consistent terminology and clear normative language. Detect
contradictions rather than allowing incompatible requirements to coexist. Resolve a conflict when the evidence
supports a coherent interpretation; otherwise place the conflicting item in the blacklist. Also blacklist
nonsensical or discarded software requirements, always with a specific reason and all source candidate IDs.
Unclear candidates must either be conservatively retained as requirements or explicitly blacklisted with a
reason; never lose them silently.

Every accepted requirement needs a short descriptive name, a paragraph-long self-contained description, and
exactly one priority using this scale:
- High: {PRIORITY_EXPLANATIONS['High']}
- Medium: {PRIORITY_EXPLANATIONS['Medium']}
- Low: {PRIORITY_EXPLANATIONS['Low']}

Every candidate ID supplied to you must appear in at least one accepted requirement or blacklist item.
Use only candidate IDs present in the input. Do not create REQ or BL IDs; Python assigns those.
Return only the structured result."""


def _invoke_refiner(model: ChatOpenAI, human_payload: dict, label: str) -> RefinementResult:
    refiner = model.with_structured_output(RefinementResult, method="json_schema")
    payload_json = json.dumps(human_payload, ensure_ascii=False)
    log(f"    sending {label} to gpt-6-luna ({len(payload_json):,} characters)")
    result = refiner.invoke(
        [
            ("system", _refinement_system_prompt()),
            ("human", payload_json),
        ]
    )
    if not isinstance(result, RefinementResult):
        result = RefinementResult.model_validate(result)
    log(
        f"    {label} returned {len(result.requirements)} requirements and "
        f"{len(result.blacklist)} blacklist items"
    )
    return result




def _represented_candidate_ids(result: RefinementResult) -> set[str]:
    return {
        candidate_id
        for item in [*result.requirements, *result.blacklist]
        for candidate_id in item.candidate_ids
    }


def _merge_refinement_results(*results: RefinementResult) -> RefinementResult:
    requirements: list[RequirementDraft] = []
    blacklist: list[BlacklistDraft] = []
    for result in results:
        requirements.extend(result.requirements)
        blacklist.extend(result.blacklist)
    return RefinementResult(requirements=requirements, blacklist=blacklist)


def _refinement_batch_cache_path(batch: list[CandidateRequirement]) -> Path:
    payload = {
        "prompt_version": REFINEMENT_PROMPT_VERSION,
        "candidates": [candidate.model_dump() for candidate in batch],
    }
    digest = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    return REFINEMENT_CACHE_DIR / f"{batch[0].candidate_id}_{batch[-1].candidate_id}_{digest}.json"


def _load_refinement_batch_cache(batch: list[CandidateRequirement]) -> RefinementResult | None:
    path = _refinement_batch_cache_path(batch)
    if not path.exists():
        return None
    try:
        result = RefinementResult.model_validate_json(path.read_text(encoding="utf-8"))
        expected = {candidate.candidate_id for candidate in batch}
        missing = expected - _represented_candidate_ids(result)
        if missing:
            log(f"    cached batch is incomplete and will be ignored ({len(missing)} missing IDs)")
            return None
        log(f"    refinement cache hit: {path.name}")
        return result
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        log(f"    refinement cache is invalid and will be ignored: {_safe_error_text(exc)}")
        return None


def _save_refinement_batch_cache(batch: list[CandidateRequirement], result: RefinementResult) -> None:
    REFINEMENT_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _refinement_batch_cache_path(batch)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    log(f"    saved refinement batch cache: {path.name}")


def _recover_missing_batch_candidates(
    model: ChatOpenAI,
    result: RefinementResult,
    batch: list[CandidateRequirement],
    batch_index: int,
    batch_count: int,
) -> RefinementResult:
    lookup = {candidate.candidate_id: candidate for candidate in batch}
    current = result

    for recovery_attempt in range(1, REFINEMENT_RECOVERY_ATTEMPTS + 1):
        represented = _represented_candidate_ids(current)
        missing_ids = sorted(set(lookup) - represented)
        if not missing_ids:
            return current

        missing_candidates = [lookup[candidate_id] for candidate_id in missing_ids]
        log(
            f"    batch {batch_index}/{batch_count} omitted {len(missing_ids)} candidate ID(s): "
            + ", ".join(missing_ids)
        )
        log(
            f"    recovery attempt {recovery_attempt}/{REFINEMENT_RECOVERY_ATTEMPTS}: "
            "sending only the missing candidate(s)"
        )
        recovery_payload = {
            "task": (
                "Classify every candidate below. Each candidate ID MUST appear in exactly one accepted "
                "requirement or blacklist item. Do not omit any supplied ID. This is a focused recovery "
                "for candidates omitted by a previous refinement call."
            ),
            "candidates": [candidate.model_dump() for candidate in missing_candidates],
        }
        recovered = _invoke_refiner(
            model,
            recovery_payload,
            f"batch {batch_index}/{batch_count} recovery {recovery_attempt}",
        )
        current = _merge_refinement_results(current, recovered)

    final_missing = sorted(set(lookup) - _represented_candidate_ids(current))
    if final_missing:
        raise ValueError(
            f"Refinement batch {batch_index} still omitted {len(final_missing)} candidate IDs after "
            f"{REFINEMENT_RECOVERY_ATTEMPTS} focused recovery attempts: "
            + ", ".join(final_missing[:20])
        )
    return current


def _compact_refinement_payload(result: RefinementResult) -> dict:
    return {
        "requirements": [item.model_dump() for item in result.requirements],
        "blacklist": [item.model_dump() for item in result.blacklist],
    }


def _result_char_size(results: list[RefinementResult]) -> int:
    payload = [_compact_refinement_payload(result) for result in results]
    return len(json.dumps(payload, ensure_ascii=False))


def _consolidate_results(
    model: ChatOpenAI, results: list[RefinementResult], expected_candidate_ids: set[str]
) -> RefinementResult:
    """Hierarchically consolidate partial refinements without one oversized request."""
    round_number = 1
    current = results

    while _result_char_size(current) > MAX_CONSOLIDATION_CHARS:
        log(
            f"  consolidation round {round_number}: {len(current)} partial results, "
            f"payload {_result_char_size(current):,} characters"
        )
        next_round: list[RefinementResult] = []
        # Consolidate a few partial outputs at a time. These payloads are much smaller
        # than the original candidate corpus because evidence text is no longer repeated.
        for group_index, group in enumerate(_chunks(current, 4), start=1):
            combined = {
                "task": "Consolidate these partial requirement sets. Merge semantic duplicates across sets, preserve all candidate IDs, resolve conflicts, and retain blacklist reasons.",
                "partial_results": [_compact_refinement_payload(item) for item in group],
            }
            next_round.append(
                _invoke_refiner(
                    model,
                    combined,
                    f"consolidation round {round_number}, group {group_index}",
                )
            )
        if len(next_round) >= len(current) and _result_char_size(next_round) >= _result_char_size(current):
            raise ValueError(
                "Refinement consolidation is not shrinking enough to fit safely in one final request. "
                "Reduce REFINEMENT_BATCH_SIZE or inspect unusually verbose model output."
            )
        current = next_round
        round_number += 1
        if round_number > 4:
            raise ValueError("Refinement consolidation exceeded the safe number of rounds")

    final_payload = {
        "task": "Produce the final globally consolidated requirement set from all partial results. Merge semantic duplicates across batches, resolve conflicts globally, preserve every candidate ID, and keep rejected items in the blacklist.",
        "partial_results": [_compact_refinement_payload(item) for item in current],
    }
    final_result = _invoke_refiner(model, final_payload, "final global consolidation")

    for recovery_attempt in range(1, REFINEMENT_RECOVERY_ATTEMPTS + 1):
        missing = sorted(expected_candidate_ids - _represented_candidate_ids(final_result))
        if not missing:
            return final_result
        log(
            f"  final consolidation omitted {len(missing)} candidate ID(s); "
            f"retry {recovery_attempt}/{REFINEMENT_RECOVERY_ATTEMPTS} with explicit missing-ID reminder"
        )
        retry_payload = {
            "task": (
                "Repair the consolidated result so that EVERY expected candidate ID is represented in an "
                "accepted requirement or blacklist item. Preserve all existing valid work and do not drop "
                "candidate IDs."
            ),
            "missing_candidate_ids": missing,
            "current_result": _compact_refinement_payload(final_result),
        }
        final_result = _invoke_refiner(
            model, retry_payload, f"final consolidation recovery {recovery_attempt}"
        )

    missing = sorted(expected_candidate_ids - _represented_candidate_ids(final_result))
    if missing:
        raise ValueError(
            f"Final consolidation still omitted {len(missing)} candidate IDs after recovery: "
            + ", ".join(missing[:20])
        )
    return final_result


def _feedback_candidate_context(state: WorkflowState) -> list[dict]:
    """Include only candidate records explicitly mentioned by reviewer feedback."""
    mentioned: set[str] = set()
    for correction in state.get("review_feedback", []):
        mentioned.update(re.findall(r"CAND-\d+", correction))
    lookup = _candidate_lookup(state)
    return [lookup[cid].model_dump() for cid in sorted(mentioned) if cid in lookup]


def _materialize_refinement(
    result: RefinementResult, state: WorkflowState
) -> tuple[list[Requirement], list[BlacklistItem]]:
    lookup = _candidate_lookup(state)

    requirement_drafts: list[tuple[RequirementDraft, list[str]]] = []
    for draft in result.requirements:
        ids = _valid_candidate_ids(draft.candidate_ids, lookup)
        if ids:
            requirement_drafts.append((draft, ids))
    requirement_drafts.sort(
        key=lambda item: (_candidate_sort_key(item[1]), item[0].name.casefold())
    )

    requirements = [
        Requirement(
            id=f"REQ-{index:03d}",
            name=draft.name.strip(),
            description=draft.description.strip(),
            priority=draft.priority,
            candidate_ids=ids,
            sources=_sources_for(ids, lookup),
        )
        for index, (draft, ids) in enumerate(requirement_drafts, start=1)
    ]

    blacklist_drafts: list[tuple[BlacklistDraft, list[str]]] = []
    for draft in result.blacklist:
        ids = _valid_candidate_ids(draft.candidate_ids, lookup)
        if ids:
            blacklist_drafts.append((draft, ids))
    blacklist_drafts.sort(
        key=lambda item: (_candidate_sort_key(item[1]), item[0].name.casefold())
    )

    blacklist = [
        BlacklistItem(
            id=f"BL-{index:03d}",
            name=draft.name.strip(),
            original_requirement=draft.original_requirement.strip(),
            sources=_sources_for(ids, lookup),
            reason=draft.reason.strip(),
            candidate_ids=ids,
        )
        for index, (draft, ids) in enumerate(blacklist_drafts, start=1)
    ]

    represented = {
        candidate_id
        for item in [*requirements, *blacklist]
        for candidate_id in item.candidate_ids
    }
    missing = [
        candidate.candidate_id
        for candidate in state["candidates"]
        if candidate.candidate_id not in represented
    ]
    if missing:
        preview = ", ".join(missing[:20])
        suffix = " ..." if len(missing) > 20 else ""
        raise ValueError(
            f"Refiner lost {len(missing)} candidate IDs ({preview}{suffix}). "
            "The workflow refuses to silently drop extracted requirements."
        )

    return requirements, blacklist


# -----------------------------------------------------------------------------
# LLM node 2: refinement
# -----------------------------------------------------------------------------

def refine_requirements(state: WorkflowState) -> dict[str, object]:
    attempt = state.get("review_attempts", 0)
    log(
        f"Stage 3/5: refining requirements with gpt-6-luna "
        f"({'initial pass' if attempt == 0 else f'feedback pass after review {attempt}'})"
    )

    # Do not pass temperature; some newer models reject unsupported sampling parameters.
    model = ChatOpenAI(model="gpt-6-luna")

    if attempt == 0 or not state.get("requirements"):
        candidates = state["candidates"]
        batches = list(_chunks(candidates, REFINEMENT_BATCH_SIZE))
        log(
            f"  {len(candidates)} candidates -> {len(batches)} refinement batches "
            f"(up to {REFINEMENT_BATCH_SIZE} candidates each)"
        )
        partial_results: list[RefinementResult] = []

        for batch_index, batch in enumerate(batches, start=1):
            log(
                f"  [refine batch {batch_index:02d}/{len(batches):02d}] "
                f"{batch[0].candidate_id}..{batch[-1].candidate_id}"
            )
            payload = {
                "task": "Refine this candidate batch. Every input candidate ID must be represented in an accepted requirement or blacklist item.",
                "candidates": [candidate.model_dump() for candidate in batch],
            }
            result = _load_refinement_batch_cache(batch)
            if result is None:
                result = _invoke_refiner(
                    model,
                    payload,
                    f"refinement batch {batch_index}/{len(batches)}",
                )
                result = _recover_missing_batch_candidates(
                    model, result, batch, batch_index, len(batches)
                )
                _save_refinement_batch_cache(batch, result)
            else:
                log(
                    f"    using cached refinement for batch {batch_index}/{len(batches)}; "
                    "no API call needed"
                )
            partial_results.append(result)

        log("  all refinement batches finished; starting global consolidation")
        result = _consolidate_results(
            model, partial_results, {candidate.candidate_id for candidate in candidates}
        )
    else:
        # Feedback loops should not re-run every batch. The reviewer is required to
        # identify affected IDs, so send the previous result plus only referenced candidates.
        log(
            f"  applying {len(state.get('review_feedback', []))} reviewer corrections "
            "without repeating initial batch refinement"
        )
        feedback_payload = {
            "task": "Repair the previous refinement according to every reviewer correction. Preserve valid prior work, all candidate IDs, source traceability, and blacklist decisions.",
            "previous_requirements": [item.model_dump() for item in state["requirements"]],
            "previous_blacklist": [item.model_dump() for item in state["blacklist"]],
            "reviewer_corrections": state.get("review_feedback", []),
            "candidates_mentioned_in_feedback": _feedback_candidate_context(state),
        }
        result = _invoke_refiner(model, feedback_payload, "review-feedback repair")

    requirements, blacklist = _materialize_refinement(result, state)
    log(
        f"Refinement complete: {len(requirements)} accepted requirements, "
        f"{len(blacklist)} blacklist items"
    )
    return {"requirements": requirements, "blacklist": blacklist}


# -----------------------------------------------------------------------------
# LLM node 3: review
# -----------------------------------------------------------------------------

def _compact_candidate_for_review(candidate: CandidateRequirement) -> dict:
    return {
        "candidate_id": candidate.candidate_id,
        "statement": candidate.statement,
        "kind": candidate.kind,
        "clarity": candidate.clarity,
        "source_path": candidate.source_path,
    }


def review_requirements(state: WorkflowState) -> dict[str, object]:
    next_attempt = state.get("review_attempts", 0) + 1
    log(f"Stage 4/5: quality review {next_attempt}/{MAX_REVIEW_ATTEMPTS} with gpt-5-mini")

    # Do not resend raw corpus text. Extraction already processed every document;
    # the compact candidate catalog is enough for coverage/traceability checks and
    # avoids the oversized request that the original implementation created.
    review_payload = {
        "candidate_catalog": [
            _compact_candidate_for_review(candidate) for candidate in state["candidates"]
        ],
        "requirements": [requirement.model_dump() for requirement in state["requirements"]],
        "blacklist": [item.model_dump() for item in state["blacklist"]],
        "source_documents": sorted({doc.source_path for doc in state["documents"]}),
    }
    payload_json = json.dumps(review_payload, ensure_ascii=False)
    log(f"  reviewer payload size: {len(payload_json):,} characters")

    model = ChatOpenAI(model="gpt-5-mini")
    reviewer = model.with_structured_output(ReviewResult, method="json_schema")
    system_prompt = """You are an independent requirements quality reviewer.
The extractor has already examined every source document separately. Compare the complete candidate catalog
with the refined requirements and blacklist. Check all nine categories in the schema: completeness, semantic
duplicates, contradictions, consistent terminology, unique requirement IDs, valid priorities, source
traceability, appropriate blacklist handling, and required short names plus paragraph-long descriptions.

For completeness, every candidate idea must be represented by an accepted requirement or justified blacklist
entry, and the final result must cover all source documents where requirements were found. Return PASS only if
every category passes. For FAIL, give concrete correction instructions and name candidate IDs or requirement IDs
wherever possible so the refiner can repair the result without receiving the entire corpus again.
Return only structured data."""

    log("  sending reviewer request ...")
    result = reviewer.invoke(
        [
            ("system", system_prompt),
            ("human", payload_json),
        ]
    )
    if not isinstance(result, ReviewResult):
        result = ReviewResult.model_validate(result)

    log(f"Review attempt {next_attempt}/{MAX_REVIEW_ATTEMPTS}: {result.verdict}")
    for check in result.checks:
        marker = "PASS" if check.passed else "FAIL"
        log(f"  {marker:4s} {check.category}: {check.details}")
    if result.corrections:
        log(f"  reviewer returned {len(result.corrections)} correction(s)")
        for correction in result.corrections:
            log(f"    - {correction}")

    return {
        "review": result,
        "review_feedback": result.corrections,
        "review_attempts": next_attempt,
    }


def route_after_review(
    state: WorkflowState,
) -> Literal["refine_requirements", "write_output"]:
    review = state.get("review")
    if (
        review
        and review.verdict == "FAIL"
        and state["review_attempts"] < MAX_REVIEW_ATTEMPTS
    ):
        log("Reviewer returned FAIL -> routing back to the refiner")
        return "refine_requirements"
    if review and review.verdict == "PASS":
        log("Reviewer returned PASS -> proceeding to final output")
    else:
        log("Maximum review attempts reached -> writing best available output")
    return "write_output"


# -----------------------------------------------------------------------------
# Deterministic output
# -----------------------------------------------------------------------------

def _format_sources(sources: list[str]) -> str:
    return ", ".join(f"`{source}`" for source in sources)


def write_output(state: WorkflowState) -> dict[str, object]:
    log("Stage 5/5: validating and writing final Markdown document")

    requirement_ids = [item.id for item in state["requirements"]]
    blacklist_ids = [item.id for item in state["blacklist"]]
    if len(requirement_ids) != len(set(requirement_ids)):
        raise ValueError("Cannot write output: duplicate requirement IDs remain")
    if len(blacklist_ids) != len(set(blacklist_ids)):
        raise ValueError("Cannot write output: duplicate blacklist IDs remain")

    for requirement in state["requirements"]:
        if not requirement.name.strip() or not requirement.description.strip():
            raise ValueError(f"Cannot write output: {requirement.id} has an empty name or description")
        if not requirement.sources:
            raise ValueError(f"Cannot write output: {requirement.id} has no source traceability")

    lines = [
        "# Software Requirements Specification",
        "",
        "## Priority Scale",
        "",
        f"- **High:** {PRIORITY_EXPLANATIONS['High']}",
        f"- **Medium:** {PRIORITY_EXPLANATIONS['Medium']}",
        f"- **Low:** {PRIORITY_EXPLANATIONS['Low']}",
        "",
        "## Requirements",
        "",
    ]

    if not state["requirements"]:
        lines.extend(["No accepted requirements were produced.", ""])

    for requirement in state["requirements"]:
        lines.extend(
            [
                f"### {requirement.id} — {requirement.name}",
                "",
                f"**Priority:** {requirement.priority}",
                "",
                f"**Sources:** {_format_sources(requirement.sources)}",
                "",
                f"**Description:** {requirement.description}",
                "",
            ]
        )

    lines.extend(["## Blacklist", ""])
    if not state["blacklist"]:
        lines.extend(["No requirements were blacklisted.", ""])

    for item in state["blacklist"]:
        lines.extend(
            [
                f"### {item.id} — {item.name}",
                "",
                f"**Original requirement:** {item.original_requirement}",
                "",
                f"**Sources:** {_format_sources(item.sources)}",
                "",
                f"**Reason:** {item.reason}",
                "",
            ]
        )

    review = state.get("review")
    lines.extend(["## Quality Review", ""])
    if review is None:
        lines.extend(["**Status:** Not completed", ""])
    elif review.verdict == "PASS":
        lines.extend(
            [f"**Status:** PASS (review attempt {state['review_attempts']})", ""]
        )
    else:
        lines.extend(
            [
                f"**Status:** FAIL after the maximum of {MAX_REVIEW_ATTEMPTS} review attempts.",
                "",
                "The document contains the best available refinement, but the reviewer reported these remaining issues:",
                "",
            ]
        )
        lines.extend(f"- {correction}" for correction in review.corrections)
        lines.append("")

    markdown = "\n".join(lines).rstrip() + "\n"
    output_path = Path(state["output_path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    log(f"Wrote final requirements document to {output_path}")
    return {"final_markdown": markdown}


# -----------------------------------------------------------------------------
# LangGraph
# -----------------------------------------------------------------------------

def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("load_documents", load_documents)
    graph.add_node("extract_requirements", extract_requirements)
    graph.add_node("refine_requirements", refine_requirements)
    graph.add_node("review_requirements", review_requirements)
    graph.add_node("write_output", write_output)

    graph.add_edge(START, "load_documents")
    graph.add_edge("load_documents", "extract_requirements")
    graph.add_edge("extract_requirements", "refine_requirements")
    graph.add_edge("refine_requirements", "review_requirements")
    graph.add_conditional_edges(
        "review_requirements",
        route_after_review,
        {
            "refine_requirements": "refine_requirements",
            "write_output": "write_output",
        },
    )
    graph.add_edge("write_output", END)
    return graph.compile()


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract and refine software requirements from a document corpus."
    )
    parser.add_argument(
        "corpus_directory",
        type=Path,
        help="Directory recursively containing .txt and .eml source documents",
    )
    parser.add_argument(
        "--refresh-extraction",
        action="store_true",
        help="Ignore extraction cache and call the extractor again for every document",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "Error: OPENAI_API_KEY is not set. Put it in Task_1/.env or export it in the shell.",
            file=sys.stderr,
        )
        return 2

    initial_state: WorkflowState = {
        "input_dir": str(args.corpus_directory),
        "output_path": str(DEFAULT_OUTPUT_PATH),
        "documents": [],
        "candidates": [],
        "requirements": [],
        "blacklist": [],
        "review": None,
        "review_feedback": [],
        "review_attempts": 0,
        "final_markdown": "",
        "refresh_extraction": bool(args.refresh_extraction),
    }

    log("Starting requirements-refinement LangGraph workflow")
    try:
        build_graph().invoke(initial_state)
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        print(f"Error: {_safe_error_text(exc)}", file=sys.stderr, flush=True)
        return 1
    except Exception as exc:
        print(
            f"Error: requirements workflow failed ({type(exc).__name__}): "
            f"{_safe_error_text(exc)}",
            file=sys.stderr,
            flush=True,
        )
        return 1

    log("Workflow completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
