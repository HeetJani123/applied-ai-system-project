"""Streamlit UI for the music recommender extension."""

from __future__ import annotations

import logging
from textwrap import dedent

import streamlit as st

from src.recommender import analyze_listening_profile


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


st.set_page_config(
    page_title="Music Recommender+",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)


SAMPLE_SCENARIOS = {
    "High-Energy Pop": {
        "profile": dedent(
            """
            Bright pop for a workout with happy hooks, fast tempo, and strong energy.
            """
        ).strip(),
    },
    "Chill Lofi": {
        "profile": dedent(
            """
            Chill lofi focus music for studying late at night with soft, acoustic textures.
            """
        ).strip(),
    },
    "Deep Intense Rock": {
        "profile": dedent(
            """
            Deep intense rock with driving guitars, powerful energy, and a heavy sound.
            """
        ).strip(),
    },
}


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-a: #07131b;
            --bg-b: #0d1f2b;
            --bg-c: #172f36;
            --panel: rgba(11, 20, 27, 0.82);
            --panel-strong: rgba(15, 25, 33, 0.96);
            --border: rgba(255, 255, 255, 0.08);
            --text: #f3f8fb;
            --muted: rgba(243, 248, 251, 0.72);
            --accent: #7be8c7;
            --accent-2: #78c7ff;
            --accent-3: #f1b86a;
        }

        .stApp {
            background:
                radial-gradient(circle at 12% 10%, rgba(123, 232, 199, 0.16), transparent 26%),
                radial-gradient(circle at 92% 8%, rgba(120, 199, 255, 0.18), transparent 20%),
                linear-gradient(180deg, var(--bg-a) 0%, var(--bg-b) 50%, var(--bg-c) 100%);
            color: var(--text);
        }

        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(7, 12, 18, 0.98), rgba(10, 16, 23, 0.96));
            border-right: 1px solid var(--border);
        }

        [data-testid="stSidebar"] * {
            color: var(--text);
        }

        .hero {
            border: 1px solid var(--border);
            border-radius: 30px;
            padding: 1.5rem 1.6rem;
            background: linear-gradient(135deg, rgba(17, 33, 40, 0.94), rgba(9, 16, 23, 0.88));
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.32);
        }

        .eyebrow {
            display: inline-block;
            padding: 0.35rem 0.75rem;
            border-radius: 999px;
            background: rgba(123, 232, 199, 0.10);
            color: #d7fff3;
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
            background: rgba(11, 18, 27, 0.78);
            box-shadow: 0 16px 46px rgba(0, 0, 0, 0.2);
        }

        .section-title {
            font-size: 1rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
            color: var(--text);
        }

        .small-note {
            color: var(--muted);
            font-size: 0.88rem;
            line-height: 1.5;
        }

        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div,
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
            box-shadow: 0 12px 28px rgba(123, 232, 199, 0.28);
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
            background: rgba(123, 232, 199, 0.13) !important;
            border-color: rgba(123, 232, 199, 0.25) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_sample(name: str) -> None:
    sample = SAMPLE_SCENARIOS[name]
    st.session_state.profile_text = sample["profile"]


def render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <span class="eyebrow">Music Recommender Extension</span>
            <h1>Turn a listening vibe into explainable song picks.</h1>
            <p>
                Describe the mood you want, and the recommender will infer genre, energy, tempo, and texture signals
                first, then rank songs from the original catalog with coverage and diversity checks.
            </p>
            <span class="mini-chip">Retrieval first</span>
            <span class="mini-chip">Explainable ranking</span>
            <span class="mini-chip">Reliability checks</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_quick_stats(analysis) -> None:
    cols = st.columns(4)
    stats = [
        ("Genre", analysis.profile.favorite_genre or "inferred"),
        ("Coverage", f"{analysis.coverage_score:.2f}"),
        ("Diversity", f"{analysis.diversity_score:.2f}"),
        ("Top songs", str(len(analysis.top_matches))),
    ]
    for col, (label, value) in zip(cols, stats):
        with col:
            st.metric(label, value)
    st.progress(min(max(analysis.coverage_score, 0.0), 1.0))


def main() -> None:
    inject_styles()
    render_hero()

    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    if "profile_text" not in st.session_state:
        load_sample("High-Energy Pop")

    sidebar_choice = st.sidebar.selectbox("Load a sample scenario", list(SAMPLE_SCENARIOS.keys()))
    if st.sidebar.button("Load sample into editor"):
        load_sample(sidebar_choice)
        st.rerun()

    st.sidebar.markdown(
        """
        <div class="section-card" style="padding: 1rem;">
          <div class="section-title">How to use it</div>
          <div class="small-note">
            Write a short vibe description, or load one of the sample profiles. The parser infers genre, mood,
            energy, tempo, and texture cues before ranking the catalog.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown('<div class="section-card" style="padding: 1rem 1rem 0.9rem 1rem;">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Input workspace</div>', unsafe_allow_html=True)
        with st.form("recommendation_form"):
            profile_text = st.text_area(
                "Describe the listening vibe",
                value=st.session_state.profile_text,
                height=220,
                placeholder="Example: Bright pop for a workout with happy hooks, fast tempo, and strong energy.",
            )
            submitted = st.form_submit_button("Generate recommendations")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card" style="padding: 1rem;">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">What the AI returns</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='small-note'>The recommender infers preference signals, ranks the catalog, and then checks whether the shortlist actually matches the requested vibe.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        analysis = analyze_listening_profile(profile_text)
        st.session_state.latest_analysis = analysis
        st.session_state.profile_text = profile_text

    analysis = st.session_state.get("latest_analysis")
    if analysis:
        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        render_quick_stats(analysis)

        st.markdown("<div style='height: 0.7rem;'></div>", unsafe_allow_html=True)
        playlist_tab, evidence_tab, reliability_tab = st.tabs(["Playlist", "Evidence", "Reliability"])

        with playlist_tab:
            st.markdown('<div class="section-card" style="padding: 1rem;">', unsafe_allow_html=True)
            st.subheader("Playlist-ready output")
            st.markdown(f"**Summary**  \n{analysis.summary}")
            st.markdown("**Recommended songs**")
            for match in analysis.top_matches:
                st.markdown(f"- {match.song.title} by {match.song.artist} ({match.song.genre}, {match.song.mood})")
            st.markdown("</div>", unsafe_allow_html=True)

        with evidence_tab:
            st.markdown('<div class="section-card" style="padding: 1rem;">', unsafe_allow_html=True)
            st.subheader("Why these songs were chosen")
            st.caption(f"Parsed profile: {analysis.profile.name}")
            for match in analysis.top_matches:
                with st.container(border=True):
                    st.caption(f"{match.song.artist} | score {match.score:.2f}")
                    st.write(match.song.title)
                    st.write("; ".join(match.reasons))
            st.markdown("</div>", unsafe_allow_html=True)

        with reliability_tab:
            st.markdown('<div class="section-card" style="padding: 1rem;">', unsafe_allow_html=True)
            st.subheader("Reliability checks")
            for check_name, passed in analysis.checks.items():
                st.write(f"{check_name}: {'pass' if passed else 'fail'}")
            if analysis.warnings:
                st.warning(" ".join(analysis.warnings))
            st.markdown("**Playlist notes**")
            for point in analysis.talking_points:
                st.write(f"- {point}")
            st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
