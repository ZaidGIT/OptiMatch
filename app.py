import streamlit as st
import docx2txt
import joblib
from utils.model import predict_resume_match, SKILLS

# ---------------- Load Models ----------------
model = joblib.load('resume_match_model.pkl')
embed_model = joblib.load('embedding_model.pkl')

# ---------------- Session State Management ----------------
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'reset_triggered' not in st.session_state:
    st.session_state.reset_triggered = False

def reset_analysis():
    st.session_state.analysis_complete = False
    st.session_state.reset_triggered = True
    st.session_state.upload_key = str(hash(str(st.session_state))) + "_reset"
    st.session_state.jd_text = ""

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="OptiMatch - Resume Intelligence",
    page_icon="●",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Professional CSS with Blue Palette ----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main{
        background-color: #1C352D;
        padding: 2rem;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #F9F6F3;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #F5C9B0;
        text-align: center;
        font-weight: 400;
        margin-bottom: 3rem;
        line-height: 1.5;
    }
    
    .metric-card {
        background-color: #A6B28B !important;
        border: 1px solid #e1e5ee;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 0.5rem;
        text-align: center;
        transition: all 0.2s ease;
        height: 100%;
        box-shadow: 0 2px 4px rgba(2, 62, 125, 0.05);
    }
    
    .metric-card:hover {
        border-color: #A6B28B;
        box-shadow: 0 4px 12px rgba(4, 102, 200, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        color: #023e7d;
        margin: 0.5rem 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: #F9F6F3;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }
    
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #e1e5ee 50%, transparent 100%);
        margin: 2.5rem 0;
        width: 100%;
    }
    
    .skill-tag {
        display: inline-block;
        background: #f8f9fc;
        color: #023e7d;
        padding: 0.35rem 0.8rem;
        border-radius: 4px;
        margin: 0.15rem;
        font-size: 0.8rem;
        font-weight: 400;
        border: 1px solid #e1e5ee;
    }
    
    .missing-skill {
        display: inline-block;
        background: #023e7d;
        color: #ffffff;
        padding: 0.35rem 0.8rem;
        border-radius: 4px;
        margin: 0.15rem;
        font-size: 0.8rem;
        font-weight: 400;
    }
    
    .analysis-card {
        background: #ffffff;
        border: 1px solid #e1e5ee;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(2, 62, 125, 0.05);
    }
    
    .progress-container {
        height: 4px;
        background: #f0f2f7;
        border-radius: 2px;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #0466c8 0%, #023e7d 100%);
        border-radius: 2px;
        transition: width 0.8s ease-in-out;
    }
    
    /* Sidebar styling - target Streamlit sidebar safely using data-testid and div fallback */
    section[data-testid="stSidebar"], div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #cccccc 0%, #1b4332 100%) !important;
        padding: 1.25rem 1rem !important;
        border-right: 1px solid #e1e5ee;
        color: #1b4332;
    }

    /* Remove inner sidebar card backgrounds so custom background shows */
    section[data-testid="stSidebar"] .css-1d391kg,
    div[data-testid="stSidebar"] .css-1d391kg,
    section[data-testid="stSidebar"] .css-18e3th9,
    div[data-testid="stSidebar"] .css-18e3th9 {
        background: transparent !important;
        box-shadow: none !important;
    }

    .stButton button {
        background: #0466c8;
        color: #ffffff;
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        background: #0353a4;
        box-shadow: 0 4px 12px rgba(4, 102, 200, 0.2);
    }
    
    .secondary-button {
        background: #ffffff !important;
        color: #0466c8 !important;
        border: 1px solid #0466c8 !important;
    }
    
    .secondary-button:hover {
        background: #f8f9fc !important;
        box-shadow: 0 4px 12px rgba(4, 102, 200, 0.1);
    }
    
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #F9F6F3;
        margin: 2rem 0 1rem 0;
        text-align: center;
    }
    
    .subsection-title {
        font-size: 1rem;
        font-weight: 500;
        color: #1C352D;
        margin: 1rem 0 0.5rem 0;
    }
    
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-match {
        background: #0466c8;
    }
    
    .status-nomatch {
        background: #979dac;
    }
    
    .sidebar-header {
        font-size: 1rem;
        font-weight: 600;
        color: #0d2818;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e1e5ee;
    }
    
    .welcome-card {
        background-color: #F9F6F3;
        border: 1px solid #e1e5ee;
        border-radius: 8px;
        padding: 3rem 2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(2, 62, 125, 0.08);
    }
    
    .input-label {
        font-size: 0.85rem;
        color: #33415c;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .success-highlight {
        background: linear-gradient(135deg, #0466c8 0%, #023e7d 100%);
        color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .stTextArea textarea, .stFileUploader button {
        border: 1px solid #e1e5ee;
        border-radius: 6px;
    }
    
    .stTextArea textarea:focus {
        border-color: #0466c8;
        box-shadow: 0 0 0 2px rgba(4, 102, 200, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Header Section ----------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="main-header">OptiMatch</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Talent and Opportunity Matching</div>', unsafe_allow_html=True)

# ---------------- Enhanced Sidebar ----------------
with st.sidebar:
    st.markdown('<div class="sidebar-header">Analysis Parameters</div>', unsafe_allow_html=True)
    
    # File Upload with proper key management
    upload_key = st.session_state.get('upload_key', 'file_uploader')
    
    st.markdown('<div class="input-label">Resume Document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Select DOCX file",
        type=["docx"],
        label_visibility="collapsed",
        key=upload_key
    )
    
    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
    
    # Job Description
    st.markdown('<div class="input-label">Job Description</div>', unsafe_allow_html=True)
    
    if 'jd_text' not in st.session_state:
        st.session_state.jd_text = ""
    
    jd_text = st.text_area(
        "Paste job description content",
        height=180,
        label_visibility="collapsed",
        placeholder="Enter the complete job description for analysis...",
        value=st.session_state.jd_text,
        key="jd_text_area"
    )
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Action Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        analyze_clicked = st.button(
            "Analyze",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        if st.button(
            "Clear",
            use_container_width=True,
            type="secondary"
        ):
            reset_analysis()
            st.rerun()

# ---------------- Main Content Logic ----------------
if analyze_clicked and uploaded_file and jd_text.strip():
    with st.spinner("Analyzing document compatibility..."):
        # Extract text and run prediction
        resume_text = docx2txt.process(uploaded_file)
        match_binary, match_prob, missing = predict_resume_match(
            resume_text, jd_text, model, embed_model
        )
        
        # Store results in session state
        st.session_state.analysis_complete = True
        st.session_state.analysis_results = {
            'match_binary': match_binary,
            'match_prob': match_prob,
            'missing': missing,
            'resume_text': resume_text,
            'jd_text': jd_text
        }

# Display results if analysis is complete
if st.session_state.get('analysis_complete', False):
    results = st.session_state.analysis_results
    match_binary = results['match_binary']
    match_prob = results['match_prob']
    missing = results['missing']
    resume_text = results['resume_text']
    jd_text = results['jd_text']
    
    # ---------------- Match Results Section ----------------
    st.markdown('<div class="section-title">Compatibility Assessment</div>', unsafe_allow_html=True)
    
    # Metrics in clean layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "status-match" if match_binary else "status-nomatch"
        status_text = "Strong Match" if match_binary else "Needs Review"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Assessment Result</div>
            <div style="margin: 1rem 0;">
                <span class="{status_color}"></span>
                <span style="color: #023e7d; font-weight: 500;">{status_text}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Compatibility Score</div>
            <div class="metric-value">{match_prob*100:.1f}%</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {match_prob*100}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Skill Gaps Identified</div>
            <div class="metric-value">{len(missing)}</div>
            <div style="font-size: 0.8rem; color: #5c677d;">
                Missing requirements
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- Skill Analysis Section ----------------
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Skill Gap Analysis</div>', unsafe_allow_html=True)
    
    if missing:
        st.markdown("""
        <div class="analysis-card">
            <div class="subsection-title">Required Skills Not Found</div>
            <div style="color: #5c677d; margin-bottom: 1rem; font-size: 0.9rem;">
                The following skills specified in the job description were not identified in your resume:
            </div>
        """, unsafe_allow_html=True)
        
        # Display missing skills in a clean grid
        cols = st.columns(3)
        for i, skill in enumerate(missing):
            with cols[i % 3]:
                st.markdown(f'<div class="missing-skill">{skill}</div>', unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="success-highlight">
            <div style="font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">Optimal Skill Alignment</div>
            <div style="font-size: 0.9rem; opacity: 0.9;">
                Your resume demonstrates comprehensive coverage of all required skills 
                specified in the job description.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- Detailed Skill Breakdown ----------------
    with st.expander("Detailed Skill Inventory", expanded=False):
        resume_skills = [skill for skill in SKILLS if skill in resume_text.lower()]
        jd_skills = [skill for skill in SKILLS if skill in jd_text.lower()]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="analysis-card">
                <div class="subsection-title">Resume Skills</div>
            """, unsafe_allow_html=True)
            
            if resume_skills:
                for skill in resume_skills:
                    st.markdown(f'<div class="skill-tag">{skill}</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="color: #5c677d; font-style: italic; font-size: 0.9rem;">
                    No specific skills identified in resume content
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="analysis-card">
                <div class="subsection-title">Job Requirements</div>
            """, unsafe_allow_html=True)
            
            if jd_skills:
                for skill in jd_skills:
                    st.markdown(f'<div class="skill-tag">{skill}</div>', unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="color: #5c677d; font-style: italic; font-size: 0.9rem;">
                    No specific skills identified in job description
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------- Reset Button ----------------
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("Start New Analysis", use_container_width=True, type="secondary"):
            reset_analysis()
            st.rerun()

else:
    # ---------------- Welcome State ----------------
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="welcome-card">
            <div style="font-size: 1.5rem; font-weight: 600; color: #1C352D; margin-bottom: 1rem;">
                Resume Compatibility Analysis
            </div>
            <div style="color: #5c677d; line-height: 1.5; margin-bottom: 2rem; font-size: 0.9rem;">
                Upload your resume and provide the job description to receive a comprehensive 
                compatibility assessment and detailed skill gap analysis.
            </div>
            <div style="border: 1px solid #F5C9B0; padding: 1rem; border-radius: 6px; background: #f8f9fc;">
                <div style="font-size: 0.85rem; color: #33415c; font-weight: 500; margin-bottom: 0.5rem;">
                    Begin Analysis
                </div>
                <div style="font-size: 0.8rem; color: #5c677d;">
                    Use the sidebar to upload documents and initiate assessment
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------------- Footer ----------------
st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #979dac; font-size: 0.75rem; padding: 1rem 0;">
    OptiMatch © 2024 • Empowering Talent Alignment
</div>
""", unsafe_allow_html=True)