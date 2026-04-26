"""Streamlit UI for the Job Application Copilot."""

from __future__ import annotations

from textwrap import dedent

import streamlit as st

from src.recommender import analyze_application


st.set_page_config(
    page_title="Job Application Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)


SAMPLE_SCENARIOS = {
    "Software Engineer": {
        "resume": dedent(
            """
            Built Python APIs for internal tools.
            Wrote automated tests for backend services.
            Collaborated with product and design teams to ship features.
            """
        ).strip(),
        "job": dedent(
            """
            Backend Engineer

            We are looking for a backend engineer with Python, FastAPI, and test automation experience.
            The role values clear communication and reliable delivery.
            """
        ).strip(),
        "notes": "We value collaboration, reliable delivery, and continuous learning.",
    },
    "Marketing Analyst": {
        "resume": dedent(
            """
            Created weekly campaign reports in Excel and dashboards.
            Presented findings to stakeholders and marketing leads.
            Improved reporting workflows with better organization.
            """
        ).strip(),
        "job": dedent(
            """
            Marketing Analyst

            Looking for a candidate with analytics, reporting, dashboards, and stakeholder communication skills.
            """
        ).strip(),
        "notes": "The team values curiosity, clarity, and strong communication.",
    },
    "Project Coordinator": {
        "resume": dedent(
            """
            Tutored students, tracked schedules, and coordinated group projects.
            Delivered presentations and managed deadlines across multiple tasks.
            """
        ).strip(),
        "job": dedent(
            """
            Project Coordinator

            This role needs organization, scheduling, communication, and leadership.
            """
        ).strip(),
        "notes": "The team is collaborative and values clear communication.",
    },
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-1: #0b1020;
            --bg-2: #121a33;
            --panel: rgba(15, 22, 44, 0.72);
            --panel-border: rgba(255, 255, 255, 0.10);
            --text-main: #f3f6ff;
            --text-soft: rgba(243, 246, 255, 0.72);
            --accent: #6ee7ff;
            --accent-2: #8b5cf6;
            --accent-3: #22c55e;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(110, 231, 255, 0.16), transparent 28%),
                radial-gradient(circle at 85% 10%, rgba(139, 92, 246, 0.18), transparent 25%),
                linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
            color: var(--text-main);
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        .hero-card {
            position: relative;
            overflow: hidden;
            border: 1px solid var(--panel-border);
            border-radius: 30px;
            background: linear-gradient(135deg, rgba(18, 26, 51, 0.88), rgba(8, 12, 24, 0.72));
            box-shadow: 0 22px 80px rgba(0, 0, 0, 0.35);
            min-height: 290px;
            animation: hero-enter 700ms ease-out both;
        }

        .hero-inner {
            position: relative;
            z-index: 2;
            padding: 2.1rem 2rem 2rem 2rem;
        }

        .eyebrow {
            display: inline-flex;
            gap: 0.5rem;
            align-items: center;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: rgba(110, 231, 255, 0.12);
            color: #aef4ff;
            font-size: 0.84rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .hero-title {
            margin: 1rem 0 0.65rem 0;
            font-size: clamp(2rem, 4vw, 4rem);
            line-height: 1;
            font-weight: 800;
            letter-spacing: -0.05em;
        }

        .hero-copy {
            max-width: 60rem;
            color: var(--text-soft);
            font-size: 1.02rem;
            line-height: 1.6;
        }

        .orb {
            position: absolute;
            border-radius: 999px;
            filter: blur(8px);
            opacity: 0.9;
            mix-blend-mode: screen;
            animation: drift 7s ease-in-out infinite;
        }

        .orb.one {
            width: 180px;
            height: 180px;
            right: -40px;
            top: -30px;
            background: radial-gradient(circle, rgba(110, 231, 255, 0.55), rgba(110, 231, 255, 0));
        }

        .orb.two {
            width: 130px;
            height: 130px;
            left: 35%;
            bottom: -20px;
            background: radial-gradient(circle, rgba(139, 92, 246, 0.52), rgba(139, 92, 246, 0));
        }

        .orb.three {
            width: 90px;
            height: 90px;
            right: 23%;
            bottom: 42px;
            background: radial-gradient(circle, rgba(34, 197, 94, 0.46), rgba(34, 197, 94, 0));
        }

        .feature-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin-top: 1.5rem;
        }

        .feature-chip {
            border: 1px solid rgba(255, 255, 255, 0.10);
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(14px);
            border-radius: 18px;
            padding: 0.85rem 1rem;
            color: var(--text-main);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.18);
            transition: transform 180ms ease, border-color 180ms ease, background 180ms ease;
        }

        .feature-chip:hover {
            transform: translateY(-2px);
            border-color: rgba(110, 231, 255, 0.25);
            background: rgba(110, 231, 255, 0.08);
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 1.25rem;
            align-items: stretch;
        }

        .hero-right {
            display: grid;
            gap: 0.85rem;
            align-content: start;
        }

        .stat-card {
            border: 1px solid rgba(255, 255, 255, 0.10);
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 1rem;
            backdrop-filter: blur(14px);
        }

        .stat-card strong {
            display: block;
            font-size: 0.92rem;
            margin-bottom: 0.25rem;
        }

        .stat-card span {
            color: var(--text-soft);
            font-size: 0.88rem;
            line-height: 1.5;
        }

        @keyframes hero-enter {
            from {
                opacity: 0;
                transform: translateY(16px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes drift {
            0%, 100% { transform: translate3d(0, 0, 0) scale(1); }
            50% { transform: translate3d(0, -10px, 0) scale(1.03); }
        }

        @media (max-width: 900px) {
            .feature-row,
            .hero-grid {
                grid-template-columns: 1fr;
            }

            .hero-inner {
                padding: 1.4rem;
            }
        }

        .feature-chip strong {
            display: block;
            font-size: 0.98rem;
            margin-bottom: 0.25rem;
        }

        .feature-chip span {
            color: var(--text-soft);
            font-size: 0.87rem;
        }

        .panel-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.8rem;
            color: var(--text-main);
        }

        .glass-panel {
            border: 1px solid var(--panel-border);
            border-radius: 24px;
            padding: 1.1rem 1.1rem 0.9rem 1.1rem;
            background: var(--panel);
            box-shadow: 0 14px 42px rgba(0, 0, 0, 0.22);
        }

        .output-box {
            border: 1px solid rgba(110, 231, 255, 0.18);
            border-left: 4px solid var(--accent);
            border-radius: 18px;
            background: rgba(110, 231, 255, 0.06);
            padding: 0.95rem 1rem;
            color: var(--text-main);
            line-height: 1.6;
        }

        .metric-label {
            color: var(--text-soft);
            font-size: 0.84rem;
            margin-bottom: 0.1rem;
        }

        .metric-value {
            color: var(--text-main);
            font-size: 1.35rem;
            font-weight: 800;
        }

        .small-note {
            color: var(--text-soft);
            font-size: 0.86rem;
        }

        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stNumberInput input {
            border-radius: 16px !important;
        }

        .stButton button {
            border-radius: 999px;
            border: 0;
            padding: 0.7rem 1.15rem;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: #08101f;
            font-weight: 800;
            box-shadow: 0 12px 30px rgba(139, 92, 246, 0.3);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
        st.markdown(
                """
                <div class="hero-card">
                    <div class="orb one"></div>
                    <div class="orb two"></div>
                    <div class="orb three"></div>
                    <div class="hero-inner">
                        <div class="hero-grid">
                            <div>
                                <div class="eyebrow">Job Application Copilot</div>
                                <div class="hero-title">Turn a resume into tailored application material.</div>
                                <div class="hero-copy">
                                    This interface uses retrieval, generation, and evaluation to help you rewrite resume bullets,
                                    draft a stronger cover-letter opener, and prepare interview talking points grounded in the job posting.
                                </div>

                                <div class="feature-row">
                                    <div class="feature-chip">
                                        <strong>Retrieval first</strong>
                                        <span>Find the lines in the resume that matter before generating advice.</span>
                                    </div>
                                    <div class="feature-chip">
                                        <strong>Guardrailed output</strong>
                                        <span>Check coverage, relevance, and factual grounding before showing results.</span>
                                    </div>
                                    <div class="feature-chip">
                                        <strong>Fast feedback</strong>
                                        <span>Use the built-in evaluation score to spot weak matches immediately.</span>
                                    </div>
                                </div>
                            </div>

                            <div class="hero-right">
                                <div class="stat-card">
                                    <strong>What it does</strong>
                                    <span>Reads a resume and job description, then generates grounded application help.</span>
                                </div>
                                <div class="stat-card">
                                    <strong>Why it matters</strong>
                                    <span>It saves time and keeps suggestions tied to real evidence instead of generic advice.</span>
                                </div>
                                <div class="stat-card">
                                    <strong>How it behaves</strong>
                                    <span>The retriever, generator, and evaluator all run together in one workflow.</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
        )


def load_sample(name: str) -> None:
    sample = SAMPLE_SCENARIOS[name]
    st.session_state.resume_text = sample["resume"]
    st.session_state.job_description = sample["job"]
    st.session_state.company_notes = sample["notes"]


def render_summary(analysis) -> None:
    cols = st.columns(4)
    metrics = [
        ("Target role", analysis.target_role),
        ("Coverage", f"{analysis.coverage_score:.2f}"),
        ("Evidence items", str(len(analysis.top_evidence))),
        ("Transferable skills", str(len(analysis.transferable_skills))),
    ]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="glass-panel">
                  <div class="metric-label">{label}</div>
                  <div class="metric-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def main() -> None:
    inject_styles()
    render_hero()

    st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

    sidebar_choice = st.sidebar.selectbox("Load a sample scenario", list(SAMPLE_SCENARIOS.keys()))
    if st.sidebar.button("Load sample into editor"):
        load_sample(sidebar_choice)

    st.sidebar.markdown(
        """
        <div class="glass-panel">
          <div class="panel-title">How to use it</div>
          <div class="small-note">
            Paste a resume and job description, optionally add company notes, then generate a tailored application plan.
            The analysis is deterministic, grounded in the provided text, and validated with guardrails.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "resume_text" not in st.session_state:
        load_sample(sidebar_choice)

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Input Workspace</div>', unsafe_allow_html=True)
        with st.form("copilot_form"):
            resume_text = st.text_area(
                "Resume",
                value=st.session_state.resume_text,
                height=220,
                placeholder="Paste the user's resume or key bullet points here.",
            )
            job_description = st.text_area(
                "Job description",
                value=st.session_state.job_description,
                height=220,
                placeholder="Paste the target job description here.",
            )
            company_notes = st.text_area(
                "Optional company notes",
                value=st.session_state.company_notes,
                height=120,
                placeholder="Add company values, mission, or recruiter notes.",
            )
            submitted = st.form_submit_button("Generate application plan")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">What the AI returns</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="small-note">
            The copilot retrieves relevant evidence first, then drafts grounded suggestions and checks coverage before presenting the result.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        analysis = analyze_application(resume_text, job_description, company_notes or None)
        st.session_state.latest_analysis = analysis

    analysis = st.session_state.get("latest_analysis")
    if analysis:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        render_summary(analysis)

        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">Top evidence retrieved</div>', unsafe_allow_html=True)
            for item in analysis.top_evidence:
                st.markdown(
                    f"""
                    <div class="output-box" style="margin-bottom: 0.75rem;">
                      <strong>{item.source.replace('_', ' ').title()}</strong><br/>
                      {item.text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">Candidate-ready output</div>', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="output-box">
                  <strong>Cover letter opening</strong><br/>
                  {analysis.cover_letter_opening}
                </div>
                <div style="height: 0.85rem;"></div>
                <div class="output-box">
                  <strong>Suggested resume bullets</strong><br/>
                  {'<br/>'.join(f'• {bullet}' for bullet in analysis.resume_bullets)}
                </div>
                <div style="height: 0.85rem;"></div>
                <div class="output-box">
                  <strong>Interview talking points</strong><br/>
                  {'<br/>'.join(f'• {point}' for point in analysis.interview_talking_points)}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if analysis.warnings:
                st.warning(" ".join(analysis.warnings))

            with st.expander("Reliability checks"):
                for check_name, passed in analysis.checks.items():
                    st.write(f"{check_name}: {'pass' if passed else 'fail'}")

            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()