# Streamlit Frontend for AI Resume Ranker

A simple and intuitive web interface for uploading resumes and job descriptions to get AI-powered analysis.

## Features

- 🔐 User authentication (Login/Register)
- 📄 PDF file upload for resume and job description
- 🤖 AI-powered resume analysis
- 📊 Similarity score display
- 📝 Detailed HR-style analysis
- 📥 Download results as JSON

## Access the Frontend

Once services are running, access the frontend at:
- **URL**: http://localhost:8501

## How to Use

1. **Start all services**:
   ```bash
   docker compose -p resumeranker up -d
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8501
   ```

3. **Register/Login**:
   - Use the sidebar to create an account or login
   - You'll receive a JWT token automatically

4. **Upload Files**:
   - Upload your resume (PDF)
   - Upload the job description (PDF)

5. **Get Analysis**:
   - Click "Rank Resume" button
   - Wait for analysis (30-60 seconds)
   - View similarity score and detailed analysis

## Running Locally (Without Docker)

If you want to run the frontend locally:

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Then access at: http://localhost:8501

## Configuration

The frontend connects to the API Gateway at `http://localhost:8080` by default.

To change the API URL, set the environment variable:
```bash
export API_GATEWAY_URL=http://your-api-gateway-url:8080
```

## Troubleshooting

- **Connection Error**: Ensure all backend services are running
- **401 Unauthorized**: Your session expired, please login again
- **File Upload Fails**: Ensure files are PDF format and under 10MB

