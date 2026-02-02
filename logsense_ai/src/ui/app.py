import streamlit as st
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from logsense_ai.src.pipeline import run_pipeline
from logsense_ai.src.models.rag_engine import RAGEngine

# Page Config
st.set_page_config(page_title="LogSense-AI", page_icon="🔍", layout="wide")

# Title
st.title("🔍 LogSense-AI: Intelligent Incident Assistant")
st.markdown("Semantic Search & Root Cause Analysis for your Logs.")

# Sidebar - Ingestion
st.sidebar.header("⚙️ Data Ingestion")

log_file_path = "logsense_ai/data/raw/app.log"
index_path = "logsense_ai/data/processed/faiss_index"

if st.sidebar.button("🔄 Run Ingestion Pipeline"):
    with st.spinner("Ingesting and processing logs..."):
        if not os.path.exists(log_file_path):
            st.sidebar.error("Log file not found! Run generator first.")
        # No API Key needed for ingestion (Local Embeddings)
        else:
            try:
                run_pipeline(log_file_path, index_path)
                st.sidebar.success("Ingestion Complete! specific Index updated.")
            except Exception as e:
                st.sidebar.error(f"Ingestion failed: {e}")

# Check Index Status
if os.path.exists(index_path):
    st.sidebar.info("✅ Vector Index Available")
else:
    st.sidebar.warning("⚠️ No Vector Index found. Please ingest logs.")

# Main Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🕵️‍♂️ Investigate Incident")
    query = st.text_input("Describe the issue (e.g., 'Why did payment fail?')", placeholder="Type your query here...")
    
    if st.button("Analyze Logs"):
        if not query:
            st.warning("Please enter a query.")
        elif not os.path.exists(index_path):
            st.error("No index found. Please run ingestion first.")
        elif not os.getenv("OPENROUTER_API_KEY"):
            st.error("Missing OPENROUTER_API_KEY.")
        else:
            with st.spinner("Analyzing logs with AI..."):
                rag = RAGEngine(index_path=index_path)
                result = rag.analyze_incident(query, k=5)
                
                st.success("Analysis Complete")
                st.markdown("### 🤖 root Cause Analysis")
                st.info(result["answer"])
                
                with st.expander("📂 View Retrieved Log Evidence"):
                    for i, log in enumerate(result["source_logs"]):
                        st.markdown(f"**Chunk {i+1}**")
                        st.code(log, language="json")

with col2:
    st.subheader("📁 System Status")
    if os.path.exists(log_file_path):
        st.success(f"Log Source: {log_file_path}")
        with open(log_file_path, "r") as f:
            lines = f.readlines()
            st.write(f"Total Lines: {len(lines)}")
            with st.expander("View Recent Raw Logs"):
                st.code("".join(lines[-10:]))
    else:
        st.error("Log Source Missing")
