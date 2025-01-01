import streamlit as st
from datetime import datetime, UTC  # Updated datetime import

# Must be the first Streamlit command
st.set_page_config(page_title="HR AI Assistant", layout="wide")

import spacy
import schedule
import time
import subprocess
import sys

# Initialize session state
if 'nlp' not in st.session_state:
    st.session_state.nlp = None

# Function to initialize spaCy
@st.cache_resource
def initialize_spacy():
    try:
        # Try to load the model
        return spacy.load("en_core_web_sm")
    except OSError:
        try:
            # If model isn't found, try downloading it
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            return spacy.load("en_core_web_sm")
        except Exception as e:
            st.error(f"Failed to load spaCy model: {str(e)}")
            st.info("Using fallback mode without NLP features")
            return None

# Initialize spaCy at startup
if st.session_state.nlp is None:
    with st.spinner('Loading NLP model...'):
        st.session_state.nlp = initialize_spacy()

# Add current date/time and user information in sidebar
st.sidebar.markdown(f"**Current Date and Time (UTC):** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.markdown(f"**User:** {st.session_state.get('user_login', 'DFalauddin')}")

# Resume Screening
class ResumeScreening:
    def __init__(self):
        self.nlp = st.session_state.nlp

    def extract_skills(self, text):
        if not self.nlp:
            return []
        doc = self.nlp(text.lower())
        # Predefined skills list for demonstration
        common_skills = {
            'python', 'java', 'javascript', 'sql', 'html', 'css', 'react',
            'machine learning', 'data analysis', 'project management',
            'communication', 'leadership', 'problem solving'
        }
        found_skills = set()
        for token in doc:
            if token.text in common_skills:
                found_skills.add(token.text)
        return list(found_skills)

    def match_skills(self, resume_skills, job_skills):
        return set(resume_skills).intersection(set(job_skills))

# [Keep your existing PayrollProcessor class here]

# [Keep your existing InterviewScheduler class here]

# [Keep your existing PerformanceTracker class here]

def main():
    st.title("HR AI Assistant")

    # Sidebar for navigation
    page = st.sidebar.selectbox(
        "Choose a function",
        ["Resume Screening", "Payroll Processing", "Interview Scheduling", "Performance Tracking"]
    )

    if page == "Resume Screening":
        st.header("Resume Screening")
        
        col1, col2 = st.columns(2)
        
        with col1:
            resume_text = st.text_area("Enter Resume Text", height=200)
        with col2:
            job_description = st.text_area("Enter Job Description", height=200)

        if st.button("Analyze Match"):
            if st.session_state.nlp:
                screener = ResumeScreening()
                resume_skills = screener.extract_skills(resume_text)
                job_skills = screener.extract_skills(job_description)
                matched_skills = screener.match_skills(resume_skills, job_skills)
                
                st.subheader("Analysis Results")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("Resume Skills")
                    st.write(resume_skills)
                
                with col2:
                    st.write("Required Skills")
                    st.write(job_skills)
                
                with col3:
                    st.write("Matched Skills")
                    st.write(list(matched_skills))
                    
                match_percentage = len(matched_skills) / len(job_skills) * 100 if job_skills else 0
                st.progress(match_percentage / 100)
                st.write(f"Match Percentage: {match_percentage:.1f}%")
            else:
                st.error("Please ensure spaCy model is properly installed")

    # [Keep your existing elif blocks for other pages]

if __name__ == "__main__":
    main()
