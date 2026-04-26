"""Command line runner for the Job Application Copilot."""

from __future__ import annotations

import logging
from textwrap import dedent

from src.recommender import analyze_application, format_analysis


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def print_analysis(label: str, resume_text: str, job_description: str, company_notes: str | None = None) -> None:
    print(f"\n=== {label} ===\n")
    analysis = analyze_application(resume_text, job_description, company_notes)
    print(format_analysis(analysis))


def main() -> None:
    scenarios = [
        (
            "Software Engineer",
            dedent(
                """
                Built Python APIs for internal tools.
                Wrote automated tests for backend services.
                Collaborated with product and design teams to ship features.
                """
            ).strip(),
            dedent(
                """
                Backend Engineer

                We are looking for a backend engineer with Python, FastAPI, and test automation experience.
                The role values clear communication and reliable delivery.
                """
            ).strip(),
            "We value collaboration, reliable delivery, and continuous learning.",
        ),
        (
            "Marketing Analyst",
            dedent(
                """
                Created weekly campaign reports in Excel and dashboards.
                Presented findings to stakeholders and marketing leads.
                Improved reporting workflows with better organization.
                """
            ).strip(),
            dedent(
                """
                Marketing Analyst

                Looking for a candidate with analytics, reporting, dashboards, and stakeholder communication skills.
                """
            ).strip(),
            None,
        ),
        (
            "Project Coordinator",
            dedent(
                """
                Tutored students, tracked schedules, and coordinated group projects.
                Delivered presentations and managed deadlines across multiple tasks.
                """
            ).strip(),
            dedent(
                """
                Project Coordinator

                This role needs organization, scheduling, communication, and leadership.
                """
            ).strip(),
            "The team is collaborative and values clear communication.",
        ),
    ]

    for label, resume_text, job_description, company_notes in scenarios:
        print_analysis(label, resume_text, job_description, company_notes)


if __name__ == "__main__":
    main()
