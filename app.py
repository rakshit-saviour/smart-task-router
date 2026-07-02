"""
Streamlit frontend for the Smart Task Router.
Talks to the FastAPI backend running locally (or deployed).
"""

import streamlit as st
import requests
import pandas as pd

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Smart Task Router", page_icon="🧭", layout="centered")

st.title("🧭 Smart Task Router")
st.caption("Routes each request to a cheap/fast model or a bigger model, based on complexity — and shows you the cost tradeoff.")

with st.form("prompt_form"):
    prompt = st.text_area("Enter your request", placeholder="e.g. Summarize the water cycle in 2 lines")
    submitted = st.form_submit_button("Route Request")

if submitted and prompt.strip():
    with st.spinner("Routing and generating response..."):
        try:
            response = requests.post(f"{BACKEND_URL}/route", json={"prompt": prompt}, timeout=30)
            if response.status_code == 200:
                result = response.json()

                st.success(f"Handled by **{result['model_used']}**  (classified as *{result['complexity']}*)")
                st.write(result["answer"])

                col1, col2, col3 = st.columns(3)
                col1.metric("Latency", f"{result['latency_seconds']}s")
                col2.metric("Tokens used", result["total_tokens"])
                col3.metric("Est. cost", f"${result['estimated_cost_usd']:.6f}")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.ConnectionError:
            st.error("Could not reach the backend. Make sure the FastAPI server is running on port 8000.")

st.divider()
st.subheader("📊 Request History")

try:
    history_response = requests.get(f"{BACKEND_URL}/history", timeout=10)
    if history_response.status_code == 200:
        history = history_response.json()
        if history:
            df = pd.DataFrame(history)
            st.dataframe(df, use_container_width=True)

            total_cost = df["estimated_cost_usd"].sum()
            st.metric("Total estimated cost so far", f"${total_cost:.6f}")
        else:
            st.info("No requests logged yet. Try one above!")
except requests.exceptions.ConnectionError:
    st.info("Backend not running yet — start it to see history here.")
