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

# Payroll Processing
class PayrollProcessor:
    def __init__(self):
        if 'payroll_records' not in st.session_state:
            st.session_state.payroll_records = []

    def calculate_net_salary(self, salary, deductions, taxes, benefits):
        return salary - deductions - taxes + benefits

    def add_employee_record(self, employee_data):
        net_salary = self.calculate_net_salary(
            employee_data['salary'],
            employee_data['deductions'],
            employee_data['taxes'],
            employee_data['benefits']
        )
        record = {
            'name': employee_data['name'],
            'salary': employee_data['salary'],
            'deductions': employee_data['deductions'],
            'taxes': employee_data['taxes'],
            'benefits': employee_data['benefits'],
            'net_salary': net_salary,
            'date_processed': datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.payroll_records.append(record)
        return record

    def get_all_records(self):
        return st.session_state.payroll_records

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

    elif page == "Payroll Processing":  # Note: This is now at the same level as the first if statement
        st.header("Payroll Processing")
        
        # Initialize PayrollProcessor
        processor = PayrollProcessor()
        
        # Create two columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Enter Employee Details")
            with st.form("payroll_form"):
                employee_name = st.text_input("Employee Name")
                salary = st.number_input("Base Salary", min_value=0.0, step=100.0)
                deductions = st.number_input("Deductions", min_value=0.0, step=10.0)
                taxes = st.number_input("Taxes", min_value=0.0, step=10.0)
                benefits = st.number_input("Benefits", min_value=0.0, step=10.0)
                
                submitted = st.form_submit_button("Process Payroll")
                if submitted and employee_name:
                    employee_data = {
                        'name': employee_name,
                        'salary': salary,
                        'deductions': deductions,
                        'taxes': taxes,
                        'benefits': benefits
                    }
                    record = processor.add_employee_record(employee_data)
                    st.success(f"Processed payroll for {employee_name}")
                    st.json(record)
        
        with col2:
            st.subheader("Payroll Records")
            records = processor.get_all_records()
            if records:
                for record in records:
                    with st.expander(f"💰 {record['name']} - {record['date_processed']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Base Salary:", f"${record['salary']:,.2f}")
                            st.write("Deductions:", f"${record['deductions']:,.2f}")
                            st.write("Taxes:", f"${record['taxes']:,.2f}")
                        with col2:
                            st.write("Benefits:", f"${record['benefits']:,.2f}")
                            st.write("Net Salary:", f"${record['net_salary']:,.2f}")
                            st.write("Date Processed:", record['date_processed'])
            else:
                st.info("No payroll records found")

    elif page == "Interview Scheduling":
        st.header("Interview Scheduling")
        st.info("Interview Scheduling feature coming soon!")

    elif page == "Performance Tracking":
        st.header("Performance Tracking")
        st.info("Performance Tracking feature coming soon!")

if __name__ == "__main__":
    main()
