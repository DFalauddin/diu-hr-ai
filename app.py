import streamlit as st
import spacy
import schedule
import time
import subprocess
import sys
from datetime import datetime

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

# Add current date/time and user information
st.sidebar.markdown(f"**Current Date and Time (UTC):** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
st.sidebar.markdown(f"**User:** {st.session_state.get('user_login', 'DFalauddin')}")

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

class PayrollProcessor:
    def __init__(self):
        self.employees = []

    def calculate_net_salary(self, salary, deductions, taxes, benefits):
        return salary - deductions - taxes + benefits

    def process_payroll(self, employee):
        net_salary = self.calculate_net_salary(
            employee['salary'],
            employee['deductions'],
            employee['taxes'],
            employee['benefits']
        )
        return {
            'name': employee['name'],
            'net_salary': net_salary,
            'processed_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

class InterviewScheduler:
    def __init__(self):
        self.interviews = []

    def add_interview(self, candidate, interviewer, date_time):
        interview = {
            'candidate': candidate,
            'interviewer': interviewer,
            'datetime': date_time,
            'status': 'Scheduled'
        }
        self.interviews.append(interview)
        return interview

class PerformanceTracker:
    def __init__(self):
        self.records = []

    def add_record(self, employee_name, metrics):
        record = {
            'employee': employee_name,
            'date': datetime.now().strftime("%Y-%m-%d"),
            'metrics': metrics
        }
        self.records.append(record)
        return record

def main():
    st.set_page_config(page_title="HR AI Assistant", layout="wide")
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

    elif page == "Payroll Processing":
        st.header("Payroll Processing")
        
        with st.form("payroll_form"):
            employee_name = st.text_input("Employee Name")
            salary = st.number_input("Base Salary", min_value=0.0)
            deductions = st.number_input("Deductions", min_value=0.0)
            taxes = st.number_input("Taxes", min_value=0.0)
            benefits = st.number_input("Benefits", min_value=0.0)
            
            submitted = st.form_submit_button("Calculate Payroll")
            
            if submitted:
                processor = PayrollProcessor()
                employee = {
                    'name': employee_name,
                    'salary': salary,
                    'deductions': deductions,
                    'taxes': taxes,
                    'benefits': benefits
                }
                result = processor.process_payroll(employee)
                
                st.success("Payroll Processed Successfully!")
                st.json(result)

    elif page == "Interview Scheduling":
        st.header("Interview Scheduling")
        
        scheduler = InterviewScheduler()
        
        with st.form("schedule_form"):
            candidate = st.text_input("Candidate Name")
            interviewer = st.text_input("Interviewer Name")
            date = st.date_input("Interview Date")
            time = st.time_input("Interview Time")
            
            submitted = st.form_submit_button("Schedule Interview")
            
            if submitted:
                datetime_str = f"{date} {time}"
                interview = scheduler.add_interview(candidate, interviewer, datetime_str)
                st.success("Interview Scheduled!")
                st.json(interview)

    elif page == "Performance Tracking":
        st.header("Performance Tracking")
        
        tracker = PerformanceTracker()
        
        with st.form("performance_form"):
            employee_name = st.text_input("Employee Name")
            productivity = st.slider("Productivity Score", 0, 100, 50)
            quality = st.slider("Quality Score", 0, 100, 50)
            attendance = st.slider("Attendance Score", 0, 100, 50)
            
            submitted = st.form_submit_button("Submit Performance Record")
            
            if submitted:
                metrics = {
                    'productivity': productivity,
                    'quality': quality,
                    'attendance': attendance,
                    'overall_score': (productivity + quality + attendance) / 3
                }
                record = tracker.add_record(employee_name, metrics)
                st.success("Performance Record Added!")
                st.json(record)

if __name__ == "__main__":
    main()
