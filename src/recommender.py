from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Sequence, Tuple
import logging
import re


logger = logging.getLogger(__name__)

STOPWORDS = {
    "a",
    "an",
    "and",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "you",
    "your",
    "role",
    "job",
    "position",
    "candidate",
    "experience",
}

SKILL_PHRASES = [
    "python",
    "fastapi",
    "api",
    "testing",
    "test automation",
    "sql",
    "excel",
    "dashboard",
    "dashboards",
    "stakeholder communication",
    "project coordination",
    "project management",
    "leadership",
    "presentation",
    "analytics",
    "data analysis",
    "reporting",
    "communication",
    "product support",
    "research",
    "collaboration",
    "customer support",
    "backend",
    "frontend",
    "automation",
]


@dataclass
class RetrievedSnippet:
    """Relevant evidence selected from the resume, job description, or notes."""

    source: str
    text: str
    score: float


@dataclass
class ApplicationAnalysis:
    """Structured output for the job application copilot."""

    target_role: str
    key_requirements: List[str]
    top_evidence: List[RetrievedSnippet]
    transferable_skills: List[str]
    resume_bullets: List[str]
    cover_letter_opening: str
    interview_talking_points: List[str]
    coverage_score: float
    warnings: List[str] = field(default_factory=list)
    checks: Dict[str, bool] = field(default_factory=dict)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _split_lines(text: str) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _tokenize(text: str) -> List[str]:
    raw_tokens = re.findall(r"[a-z0-9+.#-]+", text.lower())
    tokens: List[str] = []
    for token in raw_tokens:
        cleaned = token.strip(".,;:!?()[]{}\"'")
        if cleaned:
            tokens.append(cleaned)
    return tokens


def extract_keywords(text: str, limit: int = 8) -> List[str]:
    """Extract a compact set of keywords from text."""
    normalized = _normalize_text(text)
    keywords: List[str] = []

    for phrase in SKILL_PHRASES:
        if phrase in normalized and phrase not in keywords:
            keywords.append(phrase)

    token_counts: Dict[str, int] = {}
    for token in _tokenize(text):
        if len(token) < 3 or token in STOPWORDS:
            continue
        token_counts[token] = token_counts.get(token, 0) + 1

    for token, _count in sorted(token_counts.items(), key=lambda item: (-item[1], item[0])):
        if token not in keywords:
            keywords.append(token)
        if len(keywords) >= limit:
            break

    return keywords[:limit]


def infer_target_role(job_description: str) -> str:
    lines = _split_lines(job_description)
    if not lines:
        return "target role"
    first_line = lines[0]
    if len(first_line) <= 60:
        return first_line
    return "target role"


def score_evidence(text: str, keywords: Sequence[str]) -> float:
    normalized = _normalize_text(text)
    score = 0.0
    for keyword in keywords:
        if keyword in normalized:
            score += 2.0 if " " in keyword else 1.0
    return score


def retrieve_relevant_evidence(
    resume_text: str,
    job_description: str,
    company_notes: str | None = None,
    limit: int = 5,
) -> Tuple[List[RetrievedSnippet], List[str], str]:
    """Retrieve the most relevant resume lines for the role."""
    job_keywords = extract_keywords(job_description, limit=10)
    target_role = infer_target_role(job_description)
    evidence: List[RetrievedSnippet] = []
    normalized_target_role = _normalize_text(target_role)

    for line in _split_lines(resume_text):
        score = score_evidence(line, job_keywords)
        if score > 0:
            evidence.append(RetrievedSnippet(source="resume", text=line, score=score))

    if company_notes:
        for line in _split_lines(company_notes):
            score = score_evidence(line, job_keywords)
            if score > 0:
                evidence.append(RetrievedSnippet(source="company_notes", text=line, score=score))

    for line in _split_lines(job_description):
        normalized_line = _normalize_text(line)
        if normalized_line == normalized_target_role:
            continue
        score = score_evidence(line, job_keywords)
        if score > 0:
            evidence.append(RetrievedSnippet(source="job_description", text=line, score=score + 0.5))

    evidence.sort(key=lambda item: (-item.score, item.source, item.text))
    warnings: List[str] = []

    if not evidence:
        warnings.append("No strong matches were found, so the copilot fell back to broad resume guidance.")
        fallback_lines = _split_lines(resume_text)[:limit]
        evidence = [RetrievedSnippet(source="resume", text=line, score=0.1) for line in fallback_lines]

    return evidence[:limit], warnings, target_role


def _find_transferable_skills(resume_text: str, job_description: str) -> List[str]:
    resume_keywords = set(extract_keywords(resume_text, limit=12))
    job_keywords = set(extract_keywords(job_description, limit=12))
    overlaps = sorted(resume_keywords & job_keywords)
    if overlaps:
        return overlaps[:5]

    resume_tokens = extract_keywords(resume_text, limit=12)
    return resume_tokens[:5]


def draft_application_advice(
    target_role: str,
    evidence: Sequence[RetrievedSnippet],
    job_description: str,
    company_notes: str | None = None,
) -> Tuple[List[str], str, List[str]]:
    """Turn retrieved evidence into tailored application guidance."""
    job_keywords = extract_keywords(job_description, limit=8)
    evidence_keywords = []
    for item in evidence:
        evidence_keywords.extend(extract_keywords(item.text, limit=4))

    transferable_skills = sorted(set(evidence_keywords) & set(job_keywords))
    if not transferable_skills:
        transferable_skills = _find_transferable_skills("\n".join(item.text for item in evidence), job_description)

    top_requirements = job_keywords[:3] if job_keywords else ["relevant experience"]

    bullets: List[str] = []
    for snippet in evidence[:3]:
        bullets.append(
            f"Tailor this experience for {target_role}: {snippet.text}"
        )

    if not bullets:
        bullets.append(f"Emphasize relevant accomplishments that match the {target_role} requirements.")

    opening_focus = ", ".join(top_requirements[:2])
    cover_letter_opening = (
        f"I am excited to apply for the {target_role} role because my background aligns with {opening_focus}."
    )

    if company_notes:
        company_focus = extract_keywords(company_notes, limit=3)
        if company_focus:
            cover_letter_opening += f" I also noticed the company values {', '.join(company_focus)}."

    talking_points = [
        f"Be ready to discuss how you have used {skill} in practice." for skill in transferable_skills[:3]
    ]
    if not talking_points:
        talking_points = [
            "Be ready to explain a recent project, the tools you used, and the results you delivered.",
        ]

    return bullets, cover_letter_opening, talking_points


def evaluate_output(
    evidence: Sequence[RetrievedSnippet],
    job_description: str,
    resume_bullets: Sequence[str],
    cover_letter_opening: str,
) -> Tuple[float, Dict[str, bool], List[str]]:
    """Check whether the generated guidance is grounded and complete."""
    job_keywords = extract_keywords(job_description, limit=8)
    evidence_text = " ".join(item.text for item in evidence)
    evidence_keywords = set(extract_keywords(evidence_text, limit=12))
    covered_keywords = [keyword for keyword in job_keywords if keyword in evidence_keywords]

    coverage_score = len(covered_keywords) / max(1, len(job_keywords))
    checks = {
        "has_evidence": bool(evidence),
        "has_resume_bullets": bool(resume_bullets),
        "has_cover_letter_opening": bool(cover_letter_opening.strip()),
        "has_keyword_coverage": coverage_score >= 0.35,
    }

    warnings: List[str] = []
    if not checks["has_keyword_coverage"]:
        warnings.append("Job keyword coverage is low, so the advice may need more resume detail.")

    return coverage_score, checks, warnings


class JobApplicationCopilot:
    """Plan-act-check workflow for job application support."""

    def __init__(self, logger_instance: logging.Logger | None = None):
        self.logger = logger_instance or logger

    def analyze(
        self,
        resume_text: str,
        job_description: str,
        company_notes: str | None = None,
    ) -> ApplicationAnalysis:
        if not resume_text.strip():
            raise ValueError("resume_text must not be empty")
        if not job_description.strip():
            raise ValueError("job_description must not be empty")

        self.logger.info("Starting job application analysis")

        evidence, warnings, target_role = retrieve_relevant_evidence(
            resume_text=resume_text,
            job_description=job_description,
            company_notes=company_notes,
        )
        self.logger.info("Retrieved %d evidence items", len(evidence))

        bullets, cover_letter_opening, talking_points = draft_application_advice(
            target_role=target_role,
            evidence=evidence,
            job_description=job_description,
            company_notes=company_notes,
        )

        coverage_score, checks, evaluation_warnings = evaluate_output(
            evidence=evidence,
            job_description=job_description,
            resume_bullets=bullets,
            cover_letter_opening=cover_letter_opening,
        )

        warnings.extend(evaluation_warnings)
        transferable_skills = _find_transferable_skills(resume_text, job_description)
        key_requirements = extract_keywords(job_description, limit=6)

        if not checks["has_keyword_coverage"] and evidence:
            self.logger.info("Coverage is weak; expanding evidence in a repair pass")
            expanded_lines = _split_lines(resume_text)[:5]
            for line in expanded_lines:
                if line not in [item.text for item in evidence]:
                    evidence.append(RetrievedSnippet(source="resume", text=line, score=0.1))
            bullets, cover_letter_opening, talking_points = draft_application_advice(
                target_role=target_role,
                evidence=evidence,
                job_description=job_description,
                company_notes=company_notes,
            )
            coverage_score, checks, evaluation_warnings = evaluate_output(
                evidence=evidence,
                job_description=job_description,
                resume_bullets=bullets,
                cover_letter_opening=cover_letter_opening,
            )
            warnings.extend(evaluation_warnings)

        self.logger.info("Finished analysis with coverage score %.2f", coverage_score)

        return ApplicationAnalysis(
            target_role=target_role,
            key_requirements=key_requirements,
            top_evidence=list(evidence),
            transferable_skills=transferable_skills,
            resume_bullets=bullets,
            cover_letter_opening=cover_letter_opening,
            interview_talking_points=talking_points,
            coverage_score=coverage_score,
            warnings=warnings,
            checks=checks,
        )


def format_analysis(analysis: ApplicationAnalysis) -> str:
    """Format the analysis for CLI output."""
    lines = [f"Target role: {analysis.target_role}"]
    lines.append(f"Coverage score: {analysis.coverage_score:.2f}")
    lines.append(f"Key requirements: {', '.join(analysis.key_requirements) if analysis.key_requirements else 'none found'}")
    lines.append("")
    lines.append("Top evidence:")
    for item in analysis.top_evidence:
        lines.append(f"- [{item.source}] {item.text}")
    lines.append("")
    lines.append("Suggested resume bullets:")
    for bullet in analysis.resume_bullets:
        lines.append(f"- {bullet}")
    lines.append("")
    lines.append(f"Cover letter opening: {analysis.cover_letter_opening}")
    lines.append("")
    lines.append("Interview talking points:")
    for point in analysis.interview_talking_points:
        lines.append(f"- {point}")
    if analysis.warnings:
        lines.append("")
        lines.append("Warnings:")
        for warning in analysis.warnings:
            lines.append(f"- {warning}")
    lines.append("")
    lines.append("Checks:")
    for check_name, passed in analysis.checks.items():
        lines.append(f"- {check_name}: {'pass' if passed else 'fail'}")
    return "\n".join(lines)


def analyze_application(resume_text: str, job_description: str, company_notes: str | None = None) -> ApplicationAnalysis:
    """Convenience wrapper for the main workflow."""
    return JobApplicationCopilot().analyze(
        resume_text=resume_text,
        job_description=job_description,
        company_notes=company_notes,
    )
