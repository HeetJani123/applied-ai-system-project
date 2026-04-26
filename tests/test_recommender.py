import pytest

from src.recommender import analyze_application, retrieve_relevant_evidence


def test_retrieve_relevant_evidence_prioritizes_matching_resume_lines():
    resume_text = """
    Built Python APIs for internal tools.
    Managed team calendars and coordinated schedules.
    Wrote automated tests for backend services.
    """.strip()
    job_description = """
    Backend Engineer
    Need Python, FastAPI, and test automation.
    """.strip()

    evidence, warnings, target_role = retrieve_relevant_evidence(resume_text, job_description)

    assert target_role == "Backend Engineer"
    assert warnings == []
    assert evidence
    assert any(
        item.source == "resume" and ("Python APIs" in item.text or "automated tests" in item.text)
        for item in evidence
    )


def test_analyze_application_generates_grounded_advice():
    resume_text = """
    Created weekly campaign reports in Excel and dashboards.
    Presented findings to stakeholders and marketing leads.
    """.strip()
    job_description = """
    Marketing Analyst
    Looking for analytics, reporting, dashboards, and stakeholder communication.
    """.strip()

    analysis = analyze_application(resume_text, job_description)

    assert analysis.target_role == "Marketing Analyst"
    assert analysis.coverage_score > 0
    assert analysis.checks["has_evidence"] is True
    assert analysis.checks["has_resume_bullets"] is True
    assert analysis.cover_letter_opening.strip() != ""
    assert any("dashboard" in bullet.lower() or "stakeholder" in bullet.lower() for bullet in analysis.resume_bullets)


def test_analyze_application_is_deterministic_for_same_input():
    resume_text = """
    Tutored students, tracked schedules, and coordinated group projects.
    Delivered presentations and managed deadlines across multiple tasks.
    """.strip()
    job_description = """
    Project Coordinator
    This role needs organization, scheduling, communication, and leadership.
    """.strip()

    first = analyze_application(resume_text, job_description)
    second = analyze_application(resume_text, job_description)

    assert first == second


def test_analyze_application_rejects_empty_input():
    with pytest.raises(ValueError):
        analyze_application("", "Some job description")

    with pytest.raises(ValueError):
        analyze_application("Some resume", "")
