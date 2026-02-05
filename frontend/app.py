import streamlit as st  # type: ignore
from api_client import get_recommendations
from config import DEFAULT_TOP_K

# -------------------- PAGE CONFIG --------------------

st.set_page_config(
    page_title="Faculty Finder",
    page_icon="🎓",
    layout="wide",
)

# -------------------- CUSTOM CSS --------------------

st.markdown(
    """
    <style>
    .main {
        background-color: #f9fafb;
    }

    .title {
        font-size: 44px;
        font-weight: 800;
        text-align: center;
        margin-bottom: 5px;
    }

    .gradient-text {
        background: linear-gradient(90deg, #4f46e5, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .subtitle {
        text-align: center;
        color: #6b7280;
        margin-bottom: 30px;
        font-size: 16px;
    }

    .card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        min-height: 360px;   /* 🔥 FIXED CARD SIZE */
        box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        border-top: 4px solid #6366f1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }


    .faculty-name {
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #111827;
    }

    .faculty-email {
        font-size: 14px;
        color: #2563eb;
        margin-bottom: 14px;
    }

    .faculty-desc {
        font-size: 14.5px;
        color: #374151;
        line-height: 1.6;
        height: 110px;        /* 🔥 SAME TEXT SPACE FOR ALL */
        overflow: hidden;
    }


    .profile-btn {
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        font-weight: 600;
        color: #111827;
        background-color: #f9fafb;
        text-decoration: none;
        display: block;
    }

    .profile-btn:hover {
        background-color: #eef2ff;
        border-color: #6366f1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- HEADER --------------------

st.markdown(
    """
    <div class="title">
        Find the Right <span class="gradient-text">Faculty Expert</span>
    </div>
    <div class="subtitle">
        Semantic search to discover DAIICT faculty aligned with your research interests
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- SEARCH BAR --------------------

with st.form(key="search_form"):
    col1, col2 = st.columns([6, 1])

    with col1:
        query = st.text_input(
            "",
            placeholder="Search faculty by expertise, research interest...",
            label_visibility="collapsed",
        )

    with col2:
        search_clicked = st.form_submit_button("🔍 Search")

# -------------------- RESULTS --------------------

if search_clicked:
    if not query.strip():
        st.warning("Please enter a research interest.")
    else:
        with st.spinner("Finding best faculty matches..."):
            response = get_recommendations(
                query=query,
                top_k=DEFAULT_TOP_K,
            )

            results = response.get("results", [])

            if not results:
                st.info("No matching faculty found.")
            else:
                rows = [results[i:i + 3] for i in range(0, len(results), 3)]

                for row in rows:
                    cols = st.columns(3)

                    for col, faculty in zip(cols, row):
                        with col:
                            profile_link = faculty.get("profile_link")

                            profile_button_html = (
                                f'''
                                <a class="profile-btn" href="{profile_link}" target="_blank">
                                    Visit Profile →
                                </a>
                                '''
                                if profile_link
                                else
                                '''
                                <div class="profile-btn" style="opacity:0.5; cursor:not-allowed;">
                                    Profile Not Available
                                </div>
                                '''
                            )

                            st.markdown(
                                f"""
                                <div class="card">
                                    <div>
                                        <div class="faculty-name">{faculty['name']}</div>
                                        <div class="faculty-email">📧 {faculty.get('email', 'Not available')}</div>
                                        <div class="faculty-desc">
                                            {faculty.get('matched_text', '')[:220]}...
                                        </div>
                                    </div>

                                    {profile_button_html}
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
