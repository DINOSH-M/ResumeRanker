import streamlit as st
import requests
import json
import os
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="AI Resume Ranker",
    page_icon="📄",
    layout="wide"
)

# API Gateway URL - Use environment variable or default
# Streamlit runs server-side, so when in Docker, use service name
# When running locally, use localhost
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://localhost:8080")

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def register_user(name, email, password):
    """Register a new user"""
    try:
        response = requests.post(
            f"{API_GATEWAY_URL}/auth/register",
            json={"name": name, "email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200 or response.status_code == 201:
            data = response.json()
            return True, data.get("token"), "Registration successful!"
        else:
            return False, None, f"Registration failed: {response.text}"
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def login_user(email, password):
    """Login user and get JWT token"""
    try:
        response = requests.post(
            f"{API_GATEWAY_URL}/auth/login",
            json={"email": email, "password": password},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return True, data.get("token"), "Login successful!"
        else:
            return False, None, f"Login failed: {response.text}"
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def rank_resume(resume_file, job_description_file, token):
    """Upload resume and job description for ranking"""
    try:
        files = {
            'resume': ('resume.pdf', resume_file, 'application/pdf'),
            'job_description': ('job_description.pdf', job_description_file, 'application/pdf')
        }
        headers = {
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post(
            f"{API_GATEWAY_URL}/resume/rank",
            files=files,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            return True, response.json(), None
        else:
            return False, None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, None, f"Error: {str(e)}"

# Main App
st.title("📄 AI Resume Ranker Platform")
st.markdown("---")

# Sidebar for Authentication
with st.sidebar:
    st.header("🔐 Authentication")
    
    if not st.session_state.logged_in:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary", use_container_width=True):
                if login_email and login_password:
                    success, token, message = login_user(login_email, login_password)
                    if success:
                        st.session_state.token = token
                        st.session_state.user_email = login_email
                        st.session_state.logged_in = True
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter both email and password")
        
        with tab2:
            st.subheader("Register")
            reg_name = st.text_input("Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            
            if st.button("Register", type="primary", use_container_width=True):
                if reg_name and reg_email and reg_password:
                    success, token, message = register_user(reg_name, reg_email, reg_password)
                    if success:
                        st.session_state.token = token
                        st.session_state.user_email = reg_email
                        st.session_state.logged_in = True
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill all fields")
    else:
        st.success(f"✅ Logged in as: {st.session_state.user_email}")
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.user_email = None
            st.session_state.logged_in = False
            st.rerun()

# Main Content
if st.session_state.logged_in:
    st.header("Upload Resume & Job Description")
    st.markdown("Upload your resume and job description PDFs to get AI-powered analysis and similarity score.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Resume")
        resume_file = st.file_uploader(
            "Upload Resume (PDF)",
            type=['pdf'],
            key="resume_uploader",
            help="Upload your resume in PDF format"
        )
        if resume_file:
            st.success(f"✅ Resume uploaded: {resume_file.name}")
            st.info(f"Size: {len(resume_file.getvalue()) / 1024:.2f} KB")
    
    with col2:
        st.subheader("📋 Job Description")
        job_description_file = st.file_uploader(
            "Upload Job Description (PDF)",
            type=['pdf'],
            key="jd_uploader",
            help="Upload the job description in PDF format"
        )
        if job_description_file:
            st.success(f"✅ Job Description uploaded: {job_description_file.name}")
            st.info(f"Size: {len(job_description_file.getvalue()) / 1024:.2f} KB")
    
    st.markdown("---")
    
    # Rank Button
    if st.button("🚀 Rank Resume", type="primary", use_container_width=True, disabled=not (resume_file and job_description_file)):
        if resume_file and job_description_file:
            with st.spinner("Analyzing resume... This may take a few moments."):
                # Reset file pointers
                resume_file.seek(0)
                job_description_file.seek(0)
                
                success, result, error = rank_resume(
                    resume_file.read(),
                    job_description_file.read(),
                    st.session_state.token
                )
                
                if success:
                    st.success("✅ Analysis Complete!")
                    st.markdown("---")
                    
                    # Display Results
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        # Handle both snake_case and camelCase response formats
                        similarity_score = result.get('similarity_score') or result.get('similarityScore', 0)
                        if isinstance(similarity_score, str):
                            try:
                                similarity_score = float(similarity_score)
                            except:
                                similarity_score = 0
                        st.metric(
                            "Similarity Score",
                            f"{similarity_score:.2%}",
                            help="How well your resume matches the job description (0-100%)"
                        )
                    
                    with col2:
                        st.markdown("### 📊 Detailed Analysis")
                        st.markdown("---")
                        # Handle both snake_case and camelCase response formats
                        analysis = result.get('llm_analysis') or result.get('llmAnalysis', 'No analysis available')
                        st.markdown(f"<div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px;'>{analysis}</div>", unsafe_allow_html=True)
                    
                    # Download Results
                    results_json = json.dumps(result, indent=2)
                    st.download_button(
                        label="📥 Download Results (JSON)",
                        data=results_json,
                        file_name="resume_analysis_results.json",
                        mime="application/json"
                    )
                else:
                    st.error(f"❌ {error}")
                    if "401" in error or "Unauthorized" in error:
                        st.warning("Your session may have expired. Please log in again.")
                        st.session_state.logged_in = False
                        st.rerun()
        else:
            st.warning("⚠️ Please upload both resume and job description files")
    
    # Instructions
    with st.expander("📖 How to Use"):
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **Login/Register**: Use the sidebar to create an account or login
        2. **Upload Resume**: Upload your resume in PDF format
        3. **Upload Job Description**: Upload the job description in PDF format
        4. **Click Rank Resume**: The AI will analyze your resume against the job description
        5. **View Results**: See your similarity score and detailed HR-style analysis
        
        ### Tips:
        - Ensure both files are in PDF format
        - Maximum file size: 10MB per file
        - The analysis may take 30-60 seconds
        - Results include similarity score (0-100%) and detailed analysis
        """)
    
    # API Status Check
    with st.expander("🔍 API Status"):
        try:
            response = requests.get(f"{API_GATEWAY_URL}/auth/register", timeout=3)
            st.success("✅ API Gateway is reachable")
        except:
            st.error("❌ API Gateway is not reachable. Please ensure services are running.")
            st.info("Run: `docker compose -p resumeranker up -d`")

else:
    st.info("👆 Please login or register using the sidebar to access the resume ranking feature.")
    st.markdown("""
    ### Welcome to AI Resume Ranker Platform! 🎉
    
    This platform uses AI to analyze your resume against job descriptions and provides:
    - **Similarity Score**: How well your resume matches the job requirements
    - **HR-Style Analysis**: Detailed feedback on your resume's alignment with the job
    
    ### Features:
    - 🔐 Secure authentication with JWT tokens
    - 📄 PDF resume and job description upload
    - 🤖 AI-powered analysis using Gemini LLM
    - 📊 Cosine similarity scoring
    - 📥 Downloadable results
    
    **Get started by creating an account in the sidebar!**
    """)

