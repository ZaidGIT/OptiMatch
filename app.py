import streamlit as st
import docx2txt
import joblib
from utils.model import predict_resume_match, SKILLS

# ---------------- Load Models ----------------
model = joblib.load('resume_match_model.pkl')
embed_model = joblib.load('embedding_model.pkl')

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="OptiMatch - Bridging Talent and Opportunity with Smart Resume Matching.",
    page_icon=":briefcase:",
    layout="centered"
)

# ---------------- Hero Section ----------------
st.markdown("""
    <div style="text-align:center">
        <h1 style="color:#4B4BFF;">OptiMatch</h1>
        <h3 style="color:#333;">Professional Resume & Job Description Matching</h3>
        <p style="color:#666;">Upload a resume and paste the JD to get a match score and missing skill analysis.</p>
    </div>
""", unsafe_allow_html=True)

# ---------------- Sidebar Inputs ----------------
st.sidebar.header("Upload & Analyze")
uploaded_file = st.sidebar.file_uploader("Upload Resume (.docx)", type=["docx"])
jd_text = st.sidebar.text_area("Paste Job Description Here")

# ---------------- Analyze Button ----------------
if st.sidebar.button("Analyze Resume", key="analyze_main"):
    if uploaded_file and jd_text:
        # Extract text from uploaded file
        resume_text = docx2txt.process(uploaded_file)

        # Run prediction
        match_binary, match_prob, missing = predict_resume_match(
            resume_text, jd_text, model, embed_model
        )

        # ---------------- Display Match Results ----------------
        st.subheader("Match Results")
        st.markdown(f"**Overall Match:** {'✅ Yes' if match_binary else '❌ No'}")
        st.markdown(f"**Match Score:** {match_prob*100:.2f}%")

        # ---------------- Display Missing Skills ----------------
        st.subheader("Skill Analysis")
        if missing:
            missing_str = ", ".join([f"**<span style='color:red'>{skill}</span>**" for skill in missing])
            st.markdown("**Missing Skills from Resume (highlighted in red):**")
            st.markdown(missing_str, unsafe_allow_html=True)
        else:
            st.markdown("All JD skills are present in the resume! ✅")

        # ---------------- Optional: Show Extracted Skills ----------------
        st.subheader("Extracted Skills")
        resume_skills = [skill for skill in SKILLS if skill in resume_text.lower()]
        jd_skills = [skill for skill in SKILLS if skill in jd_text.lower()]

        st.markdown(f"**Resume Skills:** {', '.join(resume_skills) if resume_skills else 'None'}")
        st.markdown(f"**JD Skills:** {', '.join(jd_skills) if jd_skills else 'None'}")

    else:
        st.warning("Please upload a resume and paste the job description before analyzing.")
