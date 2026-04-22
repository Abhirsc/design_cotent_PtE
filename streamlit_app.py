from __future__ import annotations

import json
from datetime import datetime

import pandas as pd
import streamlit as st

from core.exporters import build_csv_bytes, build_json_bytes, build_markdown_text
from core.generator import LocalReflectionGenerator, ReflectionGenerator
from core.schemas import GenerationBatch, GenerationRequest, ReflectionEntry
from core.utils import (
    append_history,
    cleanup_expired_outputs,
    ensure_project_dirs,
    load_history,
    quality_report,
    save_batch_output,
)


st.set_page_config(
    page_title="Daily Reflection Studio",
    page_icon="🕊️",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(180deg, #f5efe4 0%, #f7f3ec 45%, #ede7dc 100%);
        color: #1f1f1f;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1f2a24 0%, #2d3a31 100%);
    }
    section[data-testid="stSidebar"] * {
        color: #f7f0e5 !important;
    }
    section[data-testid="stSidebar"] textarea::placeholder,
    section[data-testid="stSidebar"] input::placeholder {
        color: #eadfca !important;
        opacity: 1 !important;
    }
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] input {
        color: #fff9ef !important;
        -webkit-text-fill-color: #fff9ef !important;
    }
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 22px;
        background: rgba(255, 252, 246, 0.82);
        border: 1px solid rgba(54, 63, 48, 0.12);
        box-shadow: 0 18px 40px rgba(50, 43, 31, 0.08);
        margin-bottom: 1rem;
    }
    .card {
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: rgba(255, 251, 245, 0.9);
        border: 1px solid rgba(54, 63, 48, 0.12);
        margin-bottom: 0.85rem;
    }
    .eyebrow {
        letter-spacing: 0.12em;
        text-transform: uppercase;
        font-size: 0.72rem;
        color: #6a715f;
        margin-bottom: 0.3rem;
    }
    .title {
        font-size: 2.2rem;
        line-height: 1.1;
        margin-bottom: 0.5rem;
    }
</style>
"""


THEMES = [
    "Inner clarity",
    "Simplicity",
    "Stillness",
    "Letting go",
    "Daily awareness",
    "Presence in work",
    "Relationships",
    "Healing",
    "Gratitude",
    "Creative reflection",
]

PLATFORMS = ["Instagram", "LinkedIn", "X", "Threads", "Newsletter"]
TONES = ["Quiet", "Elegant", "Grounded", "Warm", "Poetic", "Minimal"]
TEMPLATES = [
    "Quote-led post",
    "Caption-led post",
    "Carousel concept",
    "Reflection prompt",
    "Weekly sequence",
]
SOUL_LEADERS = ["Kabir", "Rumi", "Lao Tzu", "Tagore", "Osho"]
ENGINES = ["OpenAI API", "Local Demo"]


def _init_state() -> None:
    if "latest_batch" not in st.session_state:
        st.session_state.latest_batch = None
    if "last_saved_path" not in st.session_state:
        st.session_state.last_saved_path = None
    if "history_before_generation" not in st.session_state:
        st.session_state.history_before_generation = []


def _render_entry(entry: ReflectionEntry, prefix: str) -> None:
    st.markdown(
        f"""
        <div class="card">
            <div class="eyebrow">{prefix}</div>
            <h3 style="margin-bottom:0.6rem;">{entry.generated_quote}</h3>
            <p><strong>Caption</strong><br>{entry.caption}</p>
            <p><strong>CTA</strong><br>{entry.cta}</p>
            <p><strong>Hashtags</strong><br>{" ".join(entry.hashtags)}</p>
            <p><strong>SEO Keywords</strong><br>{", ".join(entry.seo_keywords)}</p>
            <p><strong>Visual Direction</strong><br>{entry.visual_direction}</p>
            <p><strong>Layer Plan</strong><br>{entry.layer_plan}</p>
            <p><strong>Manual Overlay</strong><br>{entry.manual_overlay_text or "No extra overlay added yet."}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander(f"{prefix}: 5 phrase options / 5 SEO options / 5 image directions"):
        st.write("Phrase options")
        for option in entry.phrase_options:
            st.write(f"- {option}")
        st.write("SEO suggestions")
        for option in entry.seo_suggestions:
            st.write(f"- {option}")
        st.write("Image directions")
        for option in entry.image_options:
            st.write(f"- {option}")


def _history_dataframe(history: list[dict]) -> pd.DataFrame:
    rows = []
    for item in history:
        rows.append(
            {
                "created_at": item.get("created_at"),
                "theme": item.get("theme"),
                "platform": item.get("platform"),
                "tone": item.get("tone"),
                "template_type": item.get("template_type"),
                "quote": item.get("generated_quote"),
                "hashtags": " ".join(item.get("hashtags", [])),
            }
        )
    return pd.DataFrame(rows)


def _friendly_generation_error(exc: Exception) -> str:
    message = str(exc)
    lowered = message.lower()
    if "insufficient_quota" in lowered or "error code: 429" in lowered or "quota" in lowered:
        return (
            "OpenAI generation is blocked by account quota right now. "
            "You can either add billing/credits to the API account or switch the sidebar engine to Local Demo "
            "to keep testing the app without OpenAI."
        )
    if "openai_api_key is missing" in lowered:
        return "OPENAI_API_KEY is missing. Add it to `.env` before using the OpenAI API engine."
    return f"Generation failed: {exc}"


def main() -> None:
    ensure_project_dirs()
    cleanup_expired_outputs()
    _init_state()

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Daily Reflection Studio</div>
            <div class="title">Premium reflective content for calm, clear social storytelling.</div>
            <p>Create original daily posts with quote options, caption writing, hashtag ideas,
            visual direction, local history, and export-ready output.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    history = load_history()
    with st.sidebar:
        st.header("Content Controls")
        engine = st.selectbox("Generation engine", ENGINES, index=0)
        theme = st.selectbox("Theme", THEMES, index=0)
        platform = st.selectbox("Platform", PLATFORMS, index=0)
        tone = st.selectbox("Tone", TONES, index=0)
        template_type = st.selectbox("Template", TEMPLATES, index=0)
        soul_leaders = st.multiselect(
            "Soul leader influence filter",
            SOUL_LEADERS,
            default=["Kabir", "Rumi"],
            help="Choose which influence qualities should guide the writing style. The app will keep outputs original and non-quoted.",
        )
        count = st.slider("How many options?", min_value=1, max_value=5, value=3)
        weekly_plan = st.toggle("Weekly plan mode", value=False)
        manual_overlay_text = st.text_area(
            "Manual top text layer",
            placeholder="Optional final text the user wants placed on the top layer.",
            height=110,
        )
        st.caption("Generated exports older than 24 hours are cleaned from the outputs folder.")
        if engine == "Local Demo":
            st.info("Local Demo creates offline sample content for UI testing without using the OpenAI API.")

    batch_tab, history_tab, quality_tab = st.tabs(["Studio", "History", "Quality Checks"])

    with batch_tab:
        generate = st.button("Generate Content", type="primary", use_container_width=True)
        if generate:
            st.session_state.history_before_generation = history.copy()
            request = GenerationRequest(
                theme=theme,
                platform=platform,
                tone=tone,
                template_type=template_type,
                soul_leaders=soul_leaders,
                count=count,
                weekly_plan=weekly_plan,
                manual_overlay_text=manual_overlay_text.strip(),
            )
            with st.spinner("Generating reflective content..."):
                try:
                    if engine == "OpenAI API":
                        generator = ReflectionGenerator(history=st.session_state.history_before_generation)
                    else:
                        generator = LocalReflectionGenerator(history=st.session_state.history_before_generation)
                    batch = generator.generate(request)
                    st.session_state.latest_batch = batch
                    output_path = save_batch_output(batch)
                    st.session_state.last_saved_path = str(output_path)
                    append_history(batch.entries)
                    history = load_history()
                except Exception as exc:
                    st.session_state.latest_batch = None
                    st.error(_friendly_generation_error(exc))

        latest_batch: GenerationBatch | None = st.session_state.latest_batch
        if latest_batch is None:
            st.info("Choose your settings in the sidebar, then click Generate Content.")
        else:
            st.success(
                f"Created {len(latest_batch.entries)} post option(s) at "
                f"{datetime.fromisoformat(latest_batch.generated_at).strftime('%Y-%m-%d %H:%M:%S')}."
            )

            col_a, col_b, col_c = st.columns(3)
            json_bytes = build_json_bytes(latest_batch)
            csv_bytes = build_csv_bytes(latest_batch.entries)
            markdown_text = build_markdown_text(latest_batch)

            with col_a:
                st.download_button(
                    "Export JSON",
                    data=json_bytes,
                    file_name=f"reflection_batch_{latest_batch.batch_id}.json",
                    mime="application/json",
                    use_container_width=True,
                )
            with col_b:
                st.download_button(
                    "Export CSV",
                    data=csv_bytes,
                    file_name=f"reflection_batch_{latest_batch.batch_id}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            with col_c:
                st.download_button(
                    "Export Markdown",
                    data=markdown_text,
                    file_name=f"reflection_batch_{latest_batch.batch_id}.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            st.caption(f"Local batch file: {st.session_state.last_saved_path}")
            for index, entry in enumerate(latest_batch.entries, start=1):
                _render_entry(entry, prefix=f"Option {index}")

    with history_tab:
        st.subheader("Saved history")
        history = load_history()
        if not history:
            st.info("No history saved yet. Your generated posts will appear here.")
        else:
            history_df = _history_dataframe(history)
            st.dataframe(history_df, use_container_width=True, hide_index=True)
            with st.expander("Raw history JSON"):
                st.code(json.dumps(history[-10:], indent=2), language="json")

    with quality_tab:
        st.subheader("Quality checks")
        latest_batch = st.session_state.latest_batch
        if latest_batch is None:
            st.info("Generate content first to review the latest quality report.")
        else:
            comparison_history = st.session_state.history_before_generation or []
            for index, entry in enumerate(latest_batch.entries, start=1):
                report = quality_report(entry, comparison_history)
                st.markdown(f"### Option {index}")
                st.write(
                    {
                        "quote_characters": report.quote_length,
                        "caption_characters": report.caption_length,
                        "hashtag_count": report.hashtag_count,
                        "duplicate_warning": report.duplicate_warning,
                        "closest_similarity_score": round(report.closest_similarity, 3),
                    }
                )
                if report.duplicate_warning:
                    st.warning(
                        "This quote looks similar to an older saved entry. Consider regenerating or editing."
                    )


if __name__ == "__main__":
    main()
