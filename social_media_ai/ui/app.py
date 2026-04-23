"""
ui/app.py
Main Streamlit dashboard for the Social Media AI Posting System.
Fully fixed imports + production UX with image support.
"""

import sys
from pathlib import Path

# Fix imports when running via `streamlit run ui/app.py`
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from datetime import datetime
import pandas as pd

from config.settings import get_settings
from core.graph.workflow import run_pipeline
from platforms import (  # All correct spellings from platforms/__init__.py
    TwitterPoster,
    LinkedInPoster,
    InstagramPoster,
    FacebookPoster,
    ThreadsPoster,
    YouTubePoster,
    TikTokPoster,          # ← FIXED (was TiktokPoster)
)
from utils.logger import logger
from scheduler.scheduler import scheduler
from core.crews.content_crew import PlatformPost
from utils.media_handler import media_handler  # For future extensions

# Page config
st.set_page_config(
    page_title="Social Media AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🚀 Social Media AI Posting System")
st.caption("CrewAI + LangGraph + 7 Platforms • MediaHandler Ready")

# Sidebar Controls
st.sidebar.title("Configuration")
settings = get_settings()

topic = st.sidebar.text_input(
    "Topic / Campaign Idea",
    value="AI agents transforming small businesses in 2026",
    placeholder="Enter your content topic..."
)

platforms = st.sidebar.multiselect(
    "Target Platforms",
    options=settings.enabled_platforms() or ["twitter", "linkedin", "instagram", "facebook", "threads"],
    default=settings.enabled_platforms()[:4] if settings.enabled_platforms() else ["twitter", "linkedin"],
)

brand_voice = st.sidebar.text_input(
    "Brand Voice",
    value="confident, data-driven, witty",
)

require_approval = st.sidebar.checkbox("Require Human Approval", value=True)
extra_context = st.sidebar.text_area("Extra Context / Goals", height=120, placeholder="Target audience, key goals...")

if st.sidebar.button("🔥 Generate Content", type="primary", use_container_width=True):
    if not topic or not platforms:
        st.sidebar.error("Please provide a topic and at least one platform.")
    else:
        with st.spinner("Running 6-agent ContentCrew + LangGraph..."):
            try:
                result = run_pipeline(
                    topic=topic,
                    platforms=platforms,
                    brand_voice=brand_voice,
                    extra_context=extra_context,
                    require_approval=require_approval,
                )
                st.session_state.last_result = result
                st.success("✅ Content generated!")
                st.rerun()
            except Exception as e:
                logger.error(f"Generation failed: {e}")
                st.error(f"Generation failed: {e}")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Preview & Edit", "📤 Post Now", "📅 Schedule", "📊 History"])

with tab1:
    st.subheader("Content Preview & Edit")
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        content_result = result.get("content_result")
        if content_result and hasattr(content_result, "posts"):
            for plat, post in content_result.posts.items():
                with st.expander(f"📱 **{plat.upper()}** — {len(post.final_text)} chars", expanded=True):
                    edited = st.text_area("Edit post", value=post.final_text, height=180, key=f"edit_{plat}")
                    st.caption(f"Status: **{post.status}** | Issues: {post.issues or 'None'}")
                    # Image preview
                    if hasattr(post, "image_paths") and post.image_paths:
                        try:
                            st.image(post.image_paths[0], caption="Generated image", use_column_width=True)
                        except Exception:
                            st.info("Image available but preview failed.")
                    if st.button("💾 Save edits", key=f"save_{plat}"):
                        post.final_text = edited
                        st.success("✅ Saved!")
        else:
            st.info("No content yet.")
    else:
        st.info("Generate content using sidebar →")

with tab2:
    st.subheader("🚀 Post All Approved Content")
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        content_result = result.get("content_result")
        if st.button("📤 Post to All Approved Platforms Now", type="primary"):
            with st.spinner("Posting via official APIs..."):
                post_results = {}
                poster_map = {
                    "twitter": TwitterPoster(),
                    "linkedin": LinkedInPoster(),
                    "instagram": InstagramPoster(),
                    "facebook": FacebookPoster(),
                    "threads": ThreadsPoster(),
                    "youtube": YouTubePoster(),
                    "tiktok": TikTokPoster(),
                }
                approved = getattr(content_result, "approved_platforms", list(content_result.posts.keys()))
                for plat in approved:
                    post = content_result.get_post(plat) if hasattr(content_result, "get_post") else content_result.posts.get(plat)
                    if not post:
                        continue
                    try:
                        poster = poster_map.get(plat)
                        if poster:
                            res = poster.post(post)
                            post_results[plat] = res
                            st.success(f"✅ {plat.upper()}: {res.get('status')} (ID: {res.get('post_id')})")
                        else:
                            st.warning(f"⚠️ No poster for {plat}")
                    except Exception as e:
                        logger.error(f"Post failed {plat}: {e}")
                        post_results[plat] = {"status": "failed", "error": str(e)}
                        st.error(f"❌ {plat.upper()}: {e}")
                # History
                if "post_history" not in st.session_state:
                    st.session_state.post_history = []
                st.session_state.post_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "topic": topic,
                    "platforms": list(post_results.keys()),
                    "results": post_results
                })
                st.rerun()
    else:
        st.info("Generate first.")

with tab3:
    st.subheader("📅 Schedule")
    col1, col2 = st.columns(2)
    with col1: hour = st.number_input("Hour (UTC)", 0, 23, 9)
    with col2: minute = st.number_input("Minute", 0, 59, 0)
    if st.button("📅 Schedule Daily"):
        scheduler.start()
        scheduler.add_pipeline_job(topic=topic, platforms=platforms, brand_voice=brand_voice, hour=hour, minute=minute)
        st.success(f"✅ Scheduled at {hour:02d}:{minute:02d} UTC")

with tab4:
    st.subheader("📊 History")
    if "post_history" not in st.session_state:
        st.session_state.post_history = []
    if st.session_state.post_history:
        df = pd.DataFrame(st.session_state.post_history)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No posts yet.")

st.caption("Social Media AI • Fixed & Production Ready")