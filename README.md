# ⚡️ AI Data Q&A Dashboard (Groq Accelerated)

This project is a high-performance Streamlit web application designed for instant analysis and summarization of tabular data (CSV/Excel) using state-of-the-art Large Language Models (LLMs).

Unlike traditional local LLM deployments (like Ollama) that can suffer from significant latency on consumer hardware, this application leverages the Groq API to provide near-real-time data insights, making data Q&A fast and efficient.

# ✨ Key Features

Instant Analysis: Query your uploaded CSV or Excel file using natural language (e.g., "What is the average price of cars by manufacturer?").

AI-Powered Summaries: Generate a concise, actionable summary of the dataset, including core statistics and potential data quality issues, with a single click.

Secure & Fast: Uses the Groq Llama 3.1 8B Instant model, providing token generation speeds significantly higher than typical cloud or local GPU/CPU setups.

Secure Credential Management: API key is securely loaded via environment variables (GROQ_API_KEY) and is never committed to the repository.

Secrets Management

python-dotenv for local development; Render Environment Variables for deployment.

# 🚀 Getting Started (Local Setup)

Follow these steps to get the application running on your local machine.

1. Clone the Repository

git clone <YOUR_GITHUB_URL>
cd ai-data-qa-dashboard


(Note: Replace <YOUR_GITHUB_URL> with the URL of your repository.)

2. Set up Virtual Environment & Dependencies

# Create and activate the environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install all dependencies (from the generated requirements.txt)
pip install -r requirements.txt 


3. Configure Your Groq API Key

You must obtain a free API key from the Groq Console.

To run the application locally, you must create a file named .env in the root of your project directory (major project folder) and add your secret key:

# .env file content (NEVER push this file to Git)
GROQ_API_KEY="gsk_YOUR_FULL_SECRET_KEY_HERE"


4. Run the Application

Since we used python-dotenv, the key is loaded automatically when you run the app:

streamlit run app.py


The application will open in your browser at http://localhost:8501.

# ☁️ Deployment on Render

This project is configured for seamless, secure deployment on Render, as it relies entirely on environment variables.

Push to GitHub: Ensure all files except .env are pushed to your main branch (the included .gitignore handles this automatically).

Create Web Service: In the Render Dashboard, create a new Web Service linked to this GitHub repository.

Set Environment Variables: In the Environment Variables section of your Render settings, manually add your secret key:

Key: GROQ_API_KEY

Value: gsk_YOUR_FULL_SECRET_KEY_HERE (Your actual key)

Configuration: Use the following commands:

Build Command: pip install -r requirements.txt

Start Command: streamlit run app.py

Render will handle the rest, providing you with a live, serverless data dashboard!
