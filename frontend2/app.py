import sys
import os
from pathlib import Path
import streamlit as st 

# -------------------- SETUP --------------------

import sys
from pathlib import Path

# This file is in Project1/frontend2/app.py
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent  # Project1

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# Add project root to sys.path to allow imports from model and config
# This file is in Project1/frontend2/, so parent is Project1
#current_dir = Path(__file__).resolve().parent
#project_root = current_dir.parent
#if str(project_root) not in sys.path:
#    sys.path.append(str(project_root))

# Internal imports
try:
    from model.recommender import recommend_faculty, load_embeddings, load_metadata
    from config.base import FACULTY_EMBEDDINGS_PATH, FACULTY_META_PATH
    from config.settings import EMBEDDING_MODEL_NAME
    from frontend2.config import DEFAULT_TOP_K
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    st.error(f"Failed to import modules: {e}")
    st.stop()

# -------------------- CACHED RESOURCES --------------------

@st.cache_resource
def get_model():
    """Load the sentence transformer model - cached resource."""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)

@st.cache_data
def get_data():
    """Load embeddings and metadata - cached data."""
    embeddings = load_embeddings(FACULTY_EMBEDDINGS_PATH)
    metadata = load_metadata(FACULTY_META_PATH)
    return embeddings, metadata

# -------------------- PAGE CONFIG --------------------

st.set_page_config(
    page_title="Faculty Finder (Direct)",
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
        background: linear-gradient(90deg, #db2777, #9333ea); /* Different gradient for distinction */
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
        min-height: 360px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        border-top: 4px solid #db2777; /* Matching border color */
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
        height: 110px;
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
        background-color: #fdf2f8; /* Pinkish hover */
        border-color: #db2777;
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
        Direct Model Inference - Discover DAIICT faculty aligned with your research interests
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------- INITIALIZATION --------------------

with st.spinner("Loading AI Models..."):
    try:
        model = get_model()
        embeddings, metadata = get_data()
    except Exception as e:
        st.error(f"Error loading resources: {e}")
        st.stop()

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
            try:
                # Direct call to model function
                results = recommend_faculty(
                    query=query,
                    embeddings=embeddings,
                    metadata=metadata,
                    model=model,
                    top_k=DEFAULT_TOP_K,
                )

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

                                # Handle matched_text truncation
                                matched_text = faculty.get('matched_text', '')
                                if len(matched_text) > 220:
                                    matched_text = matched_text[:220] + "..."

                                st.markdown(
                                    f"""
                                    <div class="card">
                                        <div>
                                            <div class="faculty-name">{faculty['name']}</div>
                                            <div class="faculty-email">📧 {faculty.get('email', 'Not available')}</div>
                                            <div class="faculty-desc">
                                                {matched_text}
                                            </div>
                                        </div>

                                        {profile_button_html}
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
            except Exception as e:
                st.error(f"An error occurred during search: {e}")
