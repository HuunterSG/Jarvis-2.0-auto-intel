import streamlit as st
import requests
import json

# Page configuration for a professional look
st.set_page_config(
    page_title="Jarvis 2.0 | AI Collision Expert",
    page_icon="🚗",
    layout="centered"
)

# Custom CSS for industrial aesthetics
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007BFF; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 Jarvis 2.0: Automotive AI")
st.subheader("RAG-Enhanced Technical Estimation Engine")

# User Input Section
query = st.text_area(
    "Describe the vehicle damage or ask a technical question:",
    placeholder="e.g., Mixing ratio for Axalta Excel-Pro clear coat...",
    height=150
)

# Currency selector integrated into UI
currency = st.selectbox("Currency:", ["USD", "ARS", "EUR", "MXN"])

# SINGLE BUTTON LOGIC: Consolidated to prevent DuplicateElementId error
if st.button("Generate Technical Report", key="single_report_button"):
    if not query:
        st.warning("Please enter a valid damage description.")
    else:
        # We append currency instructions directly to the payload logic
        enhanced_query = f"{query}. IMPORTANT: Provide all financial costs strictly in {currency}."
        
        with st.spinner("Analyzing technical docs and calculating costs..."):
            try:
                # Backend call to local FastAPI server
                response = requests.post(
                    "http://localhost:8000/estimate", 
                    json={"description": enhanced_query},
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Analysis Complete")
                    
                    # Layout for the professional result
                    st.markdown("### 📄 Technical Estimate")
                    st.info(data['technical_estimate'])
                    
                    st.markdown("---")
                    st.caption(f"**Verification Source:** {data['data_source']}")
                else:
                    st.error(f"Backend Error: HTTP {response.status_code}")
                    st.write(response.text)
                    
            except requests.exceptions.ConnectionError:
                st.error("Connection Refused: Make sure the FastAPI server (uvicorn) is running on port 8000.")