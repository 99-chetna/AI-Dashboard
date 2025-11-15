# app.py
import streamlit as st
import pandas as pd
import textwrap
from groq import Groq 
import os # To read the API key securely

st.set_page_config(page_title="AI Data Q&A", layout="wide")
st.title("☁️ AI Data Question Answering Dashboard (Groq API)")

# ------------------------------------------
# 1. Groq Client Initialization & Security Check
# ------------------------------------------
# Retrieve API key securely from environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    # If the key is missing, halt execution and instruct the user.
    st.error("❌ GROQ_API_KEY environment variable not found.")
    st.info("Please set the variable in your terminal before running the app:\n\n`$env:GROQ_API_KEY=\"YOUR_SECRET_KEY\"`")
    st.stop()
    
# Initialize client only if key is found
GROQ_CLIENT = Groq(api_key=GROQ_API_KEY) 
MODEL_NAME = "llama-3.1-8b-instant"  # <--- UPDATED MODEL ID to fix decommissioning error

# ------------------------------------------
# 2. Utility Functions
# ------------------------------------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the dataframe by removing unnamed columns, converting dtypes,
    and forcing problematic 'object' columns to 'string' to prevent
    PyArrow serialization errors.
    """
    # Remove "Unnamed:" columns that often appear from CSVs
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    
    # Let pandas infer the best possible dtypes (e.g., to Int64, string)
    df = df.convert_dtypes() 

    # --- THIS IS THE FIX ---
    # Find any columns that are *still* 'object' type (meaning mixed types)
    # and force them to be 'string' to make them compatible with PyArrow.
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str)
        
    return df

def build_dataset_snapshot(df: pd.DataFrame, max_rows=10) -> str:
    rows_text = df.head(max_rows).to_csv(index=False)
    cols = df.columns.tolist()
    shape = df.shape
    numeric = df.select_dtypes(include=["int64", "float64", "Int64", "Float64"]).columns.tolist()
    cat = df.select_dtypes(include=["string", "object"]).columns.tolist()

    snapshot = textwrap.dedent(f"""
    Dataset shape: {shape[0]} rows x {shape[1]} columns
    Columns: {cols}
    Numeric columns: {numeric}
    Categorical/text columns: {cat}

    First {min(max_rows, len(df))} rows (CSV):
    {rows_text}
    """)
    return snapshot

def local_basic_stats_text(df: pd.DataFrame, numeric_limit=5) -> str:
    nums = df.select_dtypes(include=["int64", "float64", "Int64", "Float64"])
    if nums.shape[1] == 0:
        return "No numeric columns detected."

    stats = []
    desc = nums.describe().transpose()

    for col in desc.index[:numeric_limit]:
        mean = desc.loc[col, 'mean']
        median = nums[col].median()
        std = desc.loc[col, 'std']
        min_val = desc.loc[col, 'min']
        max_val = desc.loc[col, 'max']
        count = desc.loc[col, 'count']
        
        stats.append(f"- {col}: mean={mean:.3f}, median={median:.3f}, std={std:.3f}, min={min_val:.3f}, max={max_val:.3f}, n={count:.0f}")

    if nums.shape[1] > numeric_limit:
        stats.append(f"...and {nums.shape[1] - numeric_limit} more numeric columns.")

    return "\n".join(stats)
# ------------------------------------------


# ------------------------------------------
# 3. File Upload and Data State Management
# ------------------------------------------

# The file uploader MUST be defined early and in the main scope.
uploaded = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"]) 

# ------------------------------------------
# 4. Main Logic: Data Processing and QA Interface (ONLY runs if 'uploaded' is not None)
# ------------------------------------------
if uploaded:
    # --- File Reading and Data Preparation ---
    try:
        if uploaded.name.lower().endswith(".csv"):
            df = pd.read_csv(uploaded)
        else:
            df = pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    df = clean_dataframe(df)

    st.success("File uploaded successfully! You can now ask questions.")
    st.write(df.head()) # Display the top 5 rows

    # Generate Prompts Assets
    snapshot_text = build_dataset_snapshot(df)
    local_stats = local_basic_stats_text(df)

    st.markdown("---")
    st.subheader("🔍 Ask Any Question About the Data")

    user_question = st.text_input("Ask your question… (e.g. Which manufacturer has highest total sales?)")

    col1, col2 = st.columns([1, 1])
    with col1:
        ask_btn = st.button("Ask")
    with col2:
        summary_btn = st.button("Generate Summary")

    # ------------------------------------------
    # GROQ ASK BUTTON
    # ------------------------------------------
    if ask_btn and user_question:
        prompt = f"""
        You are a helpful data analyst. Use ONLY the dataset provided below to answer the user's question.
        Do not hallucinate. If the question is ambiguous, explicitly state assumptions and compute using the data.

        DATASET SNAPSHOT:
        {snapshot_text}

        LOCAL STATS:
        {local_stats}

        USER QUESTION:
        {user_question}

        Provide a concise, step-by-step answer explaining any computations you did.
        """

        with st.spinner("Processing with Groq (Fast API)..."):
            try:
                resp = GROQ_CLIENT.chat.completions.create(
                    model=MODEL_NAME, 
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                answer = resp.choices[0].message.content

                st.write("### 🧠 AI Answer (via Groq Llama 3.1)")
                st.write(answer)

            except Exception as e:
                st.error(f"Groq API Error: {e}")
                st.info("The model ID was deprecated. We have updated it to 'llama-3.1-8b-instant'. Please verify your Groq API key is correct.")

    # ------------------------------------------
    # GROQ SUMMARY BUTTON
    # ------------------------------------------
    if summary_btn:
        prompt = f"""
        You are a data analyst. Summarize the dataset below in plain English.
        Include: number of rows, number of columns, top 3 numeric columns by variance, any missing-data concerns,
        and 3 actionable insights the user should investigate. Use ONLY the provided data.

        DATASET SNAPSHOT:
        {snapshot_text}

        LOCAL STATS:
        {local_stats}

        Produce a short human-friendly summary (3–6 paragraphs).
        """

        with st.spinner("Generating summary with Groq (Fast API)..."):
            try:
                resp = GROQ_CLIENT.chat.completions.create(
                    model=MODEL_NAME, 
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                summary = resp.choices[0].message.content

                st.write("### 📝 Generated Summary (via Groq Llama 3.1)")
                st.write(summary)

            except Exception as e:
                st.error(f"Groq API Error: {e}")
                st.info("The model ID was deprecated. We have updated it to 'llama-3.1-8b-instant'. Please verify your Groq API key is correct.")

else:
    # 5. Message displayed on initial load before file upload
    st.info("Upload a CSV or Excel file to begin.")
    st.caption("This app uses the blazing-fast Groq API for computation.")