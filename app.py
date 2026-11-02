"""Streamlit front end:  streamlit run app.py"""
import os
from datetime import date

import streamlit as st

import config
import newsletter
import sources as src
from cli import PRESET_TOPICS
from gemini_client import GeminiNewsClient
from models import Preferences, Timeframe
from service import generate_sections

st.set_page_config(page_title="Personalized Newsletter", page_icon="📰", layout="wide")


def default_key() -> str:
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Gemini API key", value=default_key(), type="password")
    model = st.text_input("Model", value=config.MODEL)

    st.divider()
    st.subheader("Sources")
    chosen_sources = []
    for group in src.GROUP_ORDER:
        members = src.by_group(group)
        mode = st.radio(group, ["All", "Choose", "None"], horizontal=True, key=f"mode_{group}")
        if mode == "All":
            chosen_sources += members
        elif mode == "Choose":
            names = st.multiselect(f"Pick from {group.lower()}", [s.name for s in members],
                                   key=f"pick_{group}")
            chosen_sources += [s for s in members if s.name in names]

# --------------------------------------------------------------------- main
st.title("📰 Personalized Newsletter")
st.caption("Short summaries from Bengali & English newspapers and social media, with links to the full story.")

col1, col2 = st.columns(2)
with col1:
    topics = st.multiselect("Topics", PRESET_TOPICS, default=["Politics", "Sports"])
    custom = st.text_input("Custom topics (comma-separated)", placeholder="Kolkata Metro, Durga Puja")
    topics += [t.strip() for t in custom.split(",") if t.strip()]
    topics = list(dict.fromkeys(topics))

with col2:
    tf_choice = st.selectbox("Timeframe", ["Latest (48 hours)", "Past week", "Past month",
                                           "Specific year", "Custom"])
    if tf_choice == "Past week":
        timeframe = Timeframe("Past week", "published within the last 7 days")
    elif tf_choice == "Past month":
        timeframe = Timeframe("Past month", "published within the last 30 days")
    elif tf_choice == "Specific year":
        y = st.number_input("Year", min_value=1990, max_value=date.today().year,
                            value=date.today().year - 1, step=1)
        timeframe = Timeframe(f"Year {int(y)}", f"published during the calendar year {int(y)}")
    elif tf_choice == "Custom":
        text = st.text_input("Describe the period", placeholder="March 2023")
        timeframe = Timeframe(text or "Custom", f"relevant to this period: {text}")
    else:
        timeframe = Timeframe("Latest", "published within the last 48 hours (the most recent available)")

    c3, c4 = st.columns(2)
    language = c3.radio("Summary language", ["English", "Bengali"], horizontal=True)
    per_group = c4.slider("Items per topic, per group", 1, 8, 3)

if st.button("Generate newsletter", type="primary", use_container_width=True):
    if not api_key:
        st.error("Add your Gemini API key in the sidebar.")
    elif not chosen_sources:
        st.error("Select at least one source.")
    elif not topics:
        st.error("Select or type at least one topic.")
    else:
        prefs = Preferences(chosen_sources, topics, timeframe, per_group, language)
        client = GeminiNewsClient(api_key, model)
        bar = st.progress(0.0, text="Starting...")

        def on_progress(done, total, topic, group, count):
            bar.progress(done / total, text=f"{topic} / {group}: {count} item(s)")

        sections = generate_sections(prefs, client, on_progress)
        bar.empty()
        st.session_state["result"] = {
            "sections": sections,
            "md": newsletter.render_markdown(sections, prefs),
            "html": newsletter.render_html(sections, prefs),
        }

# ------------------------------------------------------------------ results
result = st.session_state.get("result")
if result:
    st.divider()
    d1, d2, _ = st.columns([1, 1, 4])
    d1.download_button("⬇ HTML", result["html"], "newsletter.html", "text/html")
    d2.download_button("⬇ Markdown", result["md"], "newsletter.md", "text/markdown")

    for sec in result["sections"]:
        st.header(sec.topic)
        for group, items in sec.by_group.items():
            st.subheader(group)
            if not items:
                st.info("Nothing found for this topic in the selected sources.")
            for it in items:
                with st.container(border=True):
                    st.caption(it.source)
                    st.markdown(f"**{it.title}**")
                    st.write(it.summary)
                    st.link_button("Read full story →", it.url)
