import streamlit as st
import requests
import json

# Configure page
st.set_page_config(page_title="Salesforce Case Mock", layout="centered")
st.title("📄 Salesforce Case Management Mock")

# Initialize state
if 'step' not in st.session_state:
    st.session_state.step = 1

# Step 1: User input
if st.session_state.step == 1:
    st.subheader("Describe the issue")
    user_input = st.text_area("Enter case details", height=150)

    if st.button("Next ➡️"):
        if not user_input.strip():
            st.warning("Please enter a case description.")
        else:
            try:
                api_url = st.secrets["doti_api"]["url"]
                api_key = st.secrets["doti_api"]["key"]

                response = requests.post(
                    api_url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={"query": user_input}
                )
                response.raise_for_status()
                st.session_state.api_result = response.json()
                st.session_state.step = 2
            except Exception as e:
                st.error(f"API request failed: {e}")

# Step 2: Show response & classify
elif st.session_state.step == 2:
    st.subheader("🔍 Doti API Response")
    st.json(st.session_state.api_result)

    st.subheader("🏷️ Classify this case")
    options = ["Deal Desk", "Sales Operations", "Billing", "Legal"]
    selected = st.multiselect("Select relevant categories", options)

    if st.button("Submit ✅"):
        st.success(f"Submitted with categories: {', '.join(selected)}")
        st.session_state.step = 1

