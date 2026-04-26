"""Streamlit UI for the Job Application Copilot."""

from __future__ import annotations

import logging
from textwrap import dedent
from typing import Optional

import streamlit as st
from pypdf import PdfReader

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    Document = None

from src.recommender import analyze_application


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


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
            --bg-a: #08111f;
            --bg-b: #0f1a30;
            --bg-c: #172443;
            --panel: rgba(13, 20, 38, 0.82);
            --panel-strong: rgba(17, 26, 49, 0.96);
            --border: rgba(255, 255, 255, 0.08);
            --text: #f4f7ff;
            --muted: rgba(244, 247, 255, 0.70);
            --accent: #75e6ff;
            --accent-2: #9b7bff;
            --accent-3: #2dd4bf;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 10%, rgba(117, 230, 255, 0.16), transparent 26%),
                radial-gradient(circle at 92% 8%, rgba(155, 123, 255, 0.18), transparent 20%),
                linear-gradient(180deg, var(--bg-a) 0%, var(--bg-b) 50%, var(--bg-c) 100%);
            color: var(--text);
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(7, 12, 24, 0.98), rgba(10, 16, 31, 0.96));
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--text);
        }

        .hero {
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.5rem 1.6rem;
            background: linear-gradient(135deg, rgba(19, 29, 56, 0.94), rgba(9, 14, 28, 0.88));
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.32);
        }

        .eyebrow {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: rgba(117, 230, 255, 0.10);
            color: #c8f8ff;
            font-size: 0.80rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .hero h1 {
            margin: 0.75rem 0 0.35rem 0;
            font-size: clamp(2rem, 4vw, 4.1rem);
            line-height: 0.98;
            letter-spacing: -0.05em;
        }

        .hero p {
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.6;
            max-width: 74ch;
        }

        .mini-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            padding: 0.55rem 0.85rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text);
            font-size: 0.88rem;
            margin-right: 0.5rem;
            margin-top: 0.4rem;
        }

        .section-card {
            border: 1px solid var(--border);
            border-radius: 24px;
            background: rgba(11, 18, 33, 0.78);
            box-shadow: 0 16px 46px rgba(0, 0, 0, 0.2);
        }

        .section-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            color: var(--text);
        }

        .metric-row {
            border: 1px solid var(--border);
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.04);
            padding: 0.3rem;
        }

        .output-box {
            border: 1px solid rgba(117, 230, 255, 0.14);
            border-radius: 18px;
            background: rgba(117, 230, 255, 0.05);
            padding: 0.95rem 1rem;
        }

        .small-note {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.5;
        }

        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
        .stFileUploader section,
        .stNumberInput input {
            border-radius: 16px !important;
        }

        .stButton button {
            border-radius: 999px;
            border: 0;
            padding: 0.7rem 1.1rem;
            background: linear-gradient(135deg, var(--accent), var(--accent-2));
            color: #07121f;
            font-weight: 800;
            box-shadow: 0 12px 28px rgba(155, 123, 255, 0.28);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 999px;
            padding: 0.5rem 0.9rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid transparent;
        }

        .stTabs [aria-selected="true"] {
            background: rgba(117, 230, 255, 0.13) !important;
            border-color: rgba(117, 230, 255, 0.25) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def extract_resume_text(uploaded_file) -> str:
    """Extract plain text from an uploaded resume file."""
    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()
    logger.info("Extracting resume text from %s", file_name)

    if file_name.endswith(".txt"):
        return uploaded_file.getvalue().decode("utf-8", errors="ignore").strip()

    if file_name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(part.strip() for part in pages if part.strip()).strip()

    if file_name.endswith(".docx"):
        if Document is None:
            raise ValueError("DOCX support is unavailable in this environment")
        document = Document(uploaded_file)
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs).strip()

    raise ValueError("Unsupported file type. Upload a .pdf, .txt, or .docx file.")


def upload_signature(uploaded_file) -> tuple[str, int]:
    """Create a lightweight signature so repeated reruns do not reprocess the same file."""
    return uploaded_file.name, uploaded_file.size


def load_sample(name: str) -> None:
    sample = SAMPLE_SCENARIOS[name]
    st.session_state.resume_text = sample["resume"]
    st.session_state.job_description = sample["job"]
    st.session_state.company_notes = sample["notes"]


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <span class="eyebrow">Job Application Copilot</span>
            <h1>Turn a resume into tailored application material.</h1>
            <p>
                Upload a resume or paste text, pair it with a job description, and the copilot will retrieve the
                strongest evidence first, then draft grounded bullet rewrites, a cover letter opening, and interview
                talking points.
            </p>
            <span class="mini-chip">Retrieval first</span>
            <span class="mini-chip">Guardrailed output</span>
            <span class="mini-chip">Reliability checks</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_stats(analysis) -> None:
    cols = st.columns(4)
    stats = [
        ("Target role", analysis.target_role),
        ("Coverage", f"{analysis.coverage_score:.2f}"),
        ("Evidence items", str(len(analysis.top_evidence))),
        ("Transferable skills", str(len(analysis.transferable_skills))),
    ]
    for col, (label, value) in zip(cols, stats):
        with col:
            st.metric(label, value)
    st.progress(min(max(analysis.coverage_score, 0.0), 1.0))


def main() -> None:
    inject_styles()
    render_hero()

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    if "resume_text" not in st.session_state:
        load_sample("Software Engineer")
    if "job_description" not in st.session_state:
        load_sample("Software Engineer")
    if "company_notes" not in st.session_state:
        load_sample("Software Engineer")

    sidebar_choice = st.sidebar.selectbox("Load a sample scenario", list(SAMPLE_SCENARIOS.keys()))
    if st.sidebar.button("Load sample into editor"):
        load_sample(sidebar_choice)
        st.rerun()

    st.sidebar.markdown(
        """
        <div class="section-card" style="padding: 1rem;">
          <div class="section-title">How to use it</div>
          <div class="small-note">
            Upload a resume, paste a job description, and optionally add company notes. The app extracts text from
            the file and fills the resume box for you.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown('<div class="section-card" style="padding: 1rem 1rem 0.9rem 1rem;">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Input workspace</div>', unsafe_allow_html=True)
        uploaded_resume = st.file_uploader(
            "Upload a resume",
            type=["pdf", "txt", "docx"],
            help="Supported formats: PDF, TXT, DOCX",
        )
        if uploaded_resume is not None:
            try:
                signature = upload_signature(uploaded_resume)
                if st.session_state.get("resume_upload_signature") != signature:
                    extracted_text = extract_resume_text(uploaded_resume)
                    st.session_state.resume_upload_signature = signature
                    if extracted_text:
                        st.session_state.resume_text = extracted_text
                        st.success(f"Loaded {uploaded_resume.name} into the resume field.")
                    else:
                        st.warning("The uploaded file did not contain readable text.")
            except Exception as exc:
                st.error(f"Could not read the uploaded resume: {exc}")

        with st.form("copilot_form"):
            resume_text = st.text_area(
                "Resume text",
                value=st.session_state.resume_text,
                height=240,
                placeholder="Paste the user's resume or upload a file above.",
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
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card" style="padding: 1rem;">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">What the AI returns</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-note'>The copilot retrieves relevant evidence first, then drafts grounded suggestions and checks coverage before presenting the result.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        analysis = analyze_application(resume_text, job_description, company_notes or None)
        st.session_state.latest_analysis = analysis

    analysis = st.session_state.get("latest_analysis")
    if analysis:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        render_quick_stats(analysis)

        st.markdown("<div style='height: 0.7rem;'></div>", unsafe_allow_html=True)
        draft_tab, evidence_tab, reliability_tab = st.tabs(["Draft", "Evidence", "Reliability"])

        with draft_tab:
            st.markdown('<div class="section-card" style="padding: 1rem;">', unsafe_allow_html=True)
            st.subheader("Candidate-ready output")
            st.markdown("**Cover letter opening**")
            st.info(analysis.cover_letter_opening)
            st.markdown("**Suggested resume bullets**")
            for bullet in analysis.resume_bullets:
                st.markdown(f"- {bullet}")
            st.markdown("**Interview talking points**")
            for point in analysis.interview_talking_points:
                st.markdown(f"- {point}")
            st.markdown("</div>", unsafe_allow_html=True)

        with evidence_tab:
            st.markdown('<div class="section-card" style="padding: 1rem;">', unsafe_allow_html=True)
            st.subheader("Top evidence retrieved")
            for item in analysis.top_evidence:
                with st.container(border=True):
                    st.caption(item.source.replace("_", " ").title())
                    st.write(item.text)
            st.markdown("</div>", unsafe_allow_html=True)

        with reliability_tab:
            st.markdown('<div class="section-card" style="padding: 1rem;">', unsafe_allow_html=True)
            st.subheader("Reliability checks")
            for check_name, passed in analysis.checks.items():
                st.write(f"{check_name}: {'pass' if passed else 'fail'}")
            if analysis.warnings:
                st.warning(" ".join(analysis.warnings))
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
