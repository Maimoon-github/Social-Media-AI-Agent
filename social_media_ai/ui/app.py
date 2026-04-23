"""
ui/app.py
Main Streamlit dashboard for the Social Media AI Posting System.
Full integration with ContentCrew, LangGraph workflow, all 7 platforms, scheduler, and utils.
"""

import streamlit as st
from datetime import datetime
import pandas as pd

from config.settings import get_settings
from core.graph.workflow import run_pipeline
from platforms import (
    TwitterPoster,
    LinkedInPoster,
    InstagramPoster,
    FacebookPoster,
    ThreadsPoster,
    YouTubePoster,
    TiktokPoster,
)
from utils.logger import logger
from scheduler.scheduler import scheduler
from core.crews.content_crew import PlatformPost

st.set_page_config(
    page_title="Social Media AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar
st.sidebar.title("🚀 Social Media AI")
st.sidebar.markdown("---")

settings = get_settings()

topic = st.sidebar.text_input("Topic / Campaign Idea", placeholder="AI agents transforming 2026 workflows")
platforms = st.sidebar.multiselect(
    "Target Platforms",
    options=settings.enabled_platforms() or ["twitter", "linkedin", "instagram"],
    default=settings.enabled_platforms()[:3] if settings.enabled_platforms() else ["twitter", "linkedin"],
    help="Only platforms with credentials in .env are shown",
)

brand_voice = st.sidebar.text_input(
    "Brand Voice",
    value="confident, data-driven, witty",
    help="Describe the tone (e.g. professional yet approachable)",
)

llm_provider = st.sidebar.selectbox(
    "LLM Provider",
    options=["ollama", "groq", "openai", "together", "anthropic"],
    index=["ollama", "groq", "openai", "together", "anthropic"].index(settings.llm_provider),
)

require_approval = st.sidebar.checkbox("Require Human Approval", value=True)
extra_context = st.sidebar.text_area("Extra Context / Goals (optional)", height=100)

st.sidebar.markdown("---")
if st.sidebar.button("🔥 Generate Content", type="primary", use_container_width=True):
    with st.spinner("Running 6-agent ContentCrew + LangGraph pipeline..."):
        result = run_pipeline(
            topic=topic,
            platforms=platforms,
            brand_voice=brand_voice,
            extra_context=extra_context,
            require_approval=require_approval,
        )
        st.session_state.last_result = result
        st.success("✅ Content generated!")

# Main area
tab1, tab2, tab3, tab4 = st.tabs(["📝 Generate & Preview", "📤 Post Now", "📅 Schedule", "📊 History"])

with tab1:
    st.subheader("Generated Content Preview")
    if "last_result" in st.session_state:
        result = st.session_state.last_result
        content_result = result.get("content_result")

        if content_result:
            for platform_name, post in content_result.posts.items():
                with st.expander(f"📱 {platform_name.upper()} — {len(post.final_text)} chars", expanded=True):
                    edited_text = st.text_area(
                        f"Edit {platform_name} post",
                        value=post.final_text,
                        height=200,
                        key=f"edit_{platform_name}",
                    )
                    st.caption(f"Status: **{post.status}** | Issues: {post.issues or 'None'}")
                    if st.button(f"💾 Save changes to {platform_name}", key=f"save_{platform_name}"):
                        post.final_text = edited_text
                        st.success("Changes saved!")
    else:
        st.info("Generate content on the sidebar to see previews here.")

with tab2:
    st.subheader("Post to Platforms Now")
    if "last_result" in st.session_state and st.button("🚀 Post All Approved Content", type="primary"):
        result = st.session_state.last_result
        content_result = result.get("content_result")
        if content_result:
            with st.spinner("Posting to all platforms..."):
                post_results = {}
                for platform_name, post in content_result.posts.items():
                    if post.status == "APPROVED":
                        try:
                            poster_map = {
                                "twitter": TwitterPoster(),
                                "linkedin": LinkedInPoster(),
                                "instagram": InstagramPoster(),
                                "facebook": FacebookPoster(),
                                "threads": ThreadsPoster(),
                                "youtube": YouTubePoster(),
                                "tiktok": TiktokPoster(),
                            }
                            poster = poster_map.get(platform_name)
                            if poster:
                                res = poster.post(post)
                                post_results[platform_name] = res
                                st.success(f"✅ Posted to {platform_name}")
                        except Exception as e:
                            st.error(f"❌ {platform_name}: {e}")
                st.session_state.post_history = st.session_state.get("post_history", []) + [
                    {"timestamp": datetime.now(), "topic": topic, "results": post_results}
                ]
    else:
        st.info("Generate and approve content first.")

with tab3:
    st.subheader("Schedule Future Posts")
    col1, col2 = st.columns(2)
    with col1:
        hour = st.number_input("Hour (UTC)", min_value=0, max_value=23, value=9)
    with col2:
        minute = st.number_input("Minute", min_value=0, max_value=59, value=0)

    if st.button("📅 Schedule Daily Post"):
        scheduler.start()
        job_id = scheduler.add_pipeline_job(
            topic=topic,
            platforms=platforms,
            brand_voice=brand_voice,
            hour=hour,
            minute=minute,
        )
        st.success(f"✅ Job scheduled: {job_id}")

with tab4:
    st.subheader("Post History")
    if "post_history" in st.session_state:
        df = pd.DataFrame(st.session_state.post_history)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No posts yet.")

# Footer
st.caption("Social Media AI • Powered by CrewAI + LangGraph + Ollama/Groq")