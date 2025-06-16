import streamlit as st
import requests
import json
import time
import threading

# --- 0.1 Page Setup ---
st.set_page_config(page_title="Salesforce Case Mock", layout="wide")
st.markdown("<h1 style='text-align: center;'>📄 Sales Operations & Deal Desk Cases</h1>", unsafe_allow_html=True)

# --- 0.2 Intro ---
st.markdown("""
<div style="background-color: #005fb2; padding: 1em; border-radius: 6px; color: white;">
    <h3>👋 Dear GTM User! To get your problem solved, you can go through the flow below:</h3>
    <ol>
        <li><strong>Step 1 - Query Doti (Our AI Agent):</strong> Get an <u>instant answer</u> to your Sales Ops or Deal Desk question by describing your issue below.</li>
        <li><strong>Step 2 - Submit a Case:</strong> If your question requires Sales Operations OR Deal Desk active support, you can open a case using the regular process.</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# --- 0.3 Styling ---
st.markdown("""<style>
    .main, .stApp { background-color: #0070d2; color: white; }
    .stTextArea textarea, .stButton button { background-color: white; color: black; }
    .stSelectbox div[data-baseweb="select"], .stSelectbox div[data-baseweb="select"] * {
        background-color: transparent !important;
        color: black !important;
    }
    h1, h2, h3, h4, label { color: white !important; }
    a { color: yellow !important; }
    .stAlert[data-testid="stAlert-info"] {
        background-color: #1b74e4 !important;
        color: white !important;
        border: none;
    }
    .stAlert[data-testid="stAlert-info"] p,
    .stAlert[data-testid="stAlert-info"] span,
    .stAlert[data-testid="stAlert-info"] strong {
        color: white !important;
    }
                .stTextArea textarea, .stTextInput input, .stSelectbox, .stButton button {
        width: 100% !important;
    }
    .stButton > button {
        display: block;
        margin: auto;
        width: 100%;
    }
</style>""", unsafe_allow_html=True)


# --- 0.4 State Setup ---
if 'api_result' not in st.session_state:
    st.session_state.api_result = None
if 'response_time' not in st.session_state:
    st.session_state.response_time = None
if "submitted_query" not in st.session_state:
    st.session_state.submitted_query = False
if "show_right_col" not in st.session_state:
    st.session_state.show_right_col = False

# --- Section 1: DOTI API ---
st.subheader("🤖 What is the current issue you have?")
center_col = st.columns([1, 2, 1])[1]

with center_col:
    user_input = st.text_area("Ask your question:", height=70)
    if st.button("Submit Your Question To Doti (5-15 Seconds) ➡️"):
        if not user_input.strip():
            st.warning("Please enter a case description.")
        else:
            result_container = {}
            placeholder = st.empty()
            start_time = time.time()

            def make_request():
                try:
                    api_url = st.secrets["doti_api"]["url"]
                    api_key = st.secrets["doti_api"]["key"]
                    response = requests.post(
                        api_url,
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        json={"query": user_input}
                    )
                    response.raise_for_status()
                    result_container['response'] = response.json()
                    result_container['success'] = True
                except Exception as e:
                    result_container['error'] = str(e)
                    result_container['success'] = False

            thread = threading.Thread(target=make_request)
            thread.start()

            while thread.is_alive():
                elapsed = int(time.time() - start_time)
                placeholder.markdown(f"""
                 <div style="background-color: #1b74e4; padding: 1em; border-radius: 5px; color: white; text-align: center;">
                  ⏱️ Waiting for Doti to respond... {elapsed} seconds elapsed.
                 </div>
                """, unsafe_allow_html=True)
                time.sleep(1)

            placeholder.empty()

            if result_container.get("success"):
                st.session_state.api_result = result_container["response"]
                st.session_state.response_time = time.time() - start_time
                st.session_state.submitted_query = True
                st.markdown(f"""
                 <div style="background-color: #1b74e4; padding: 1em; border-radius: 5px; color: white; font-weight: 500;">
                  ✅ Doti responded in {st.session_state.response_time:.2f} seconds.
                 </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"API request failed: {result_container.get('error')}")

if st.session_state.api_result:
    with center_col:
        resp = st.session_state.api_result
        st.markdown(f"### ❓ Question:\n{resp.get('question', 'N/A')}")
        st.markdown(f"### 🧠 Answer:\n{resp.get('answer', 'N/A')}")
        sources = resp.get("sources", [])
        if sources:
            st.markdown("### 📚 Sources:")
            for idx, s in enumerate(sources, 1):
                st.markdown(f"**{idx}. {s.get('name')}**  \n🔗 [View Source]({s.get('link')})  \n📊 Relevancy: {s.get('relevancy', 'N/A')}")
        else:
            st.markdown("_No sources provided._")

if st.session_state.submitted_query:
    with center_col:
        if st.button("👋 This doesn't help. I need assistance from real person!"):
            st.session_state.show_right_col = True
        if st.button("🔄 This helps a bit. I'd like to ask the AI Agent another question"):
            st.session_state.api_result = None
            st.session_state.submitted_query = False
            st.session_state.response_time = None
            st.rerun()

# --- Section 2: New Case ---
if st.session_state.show_right_col:
    with center_col:
        st.subheader("📬 Open New Sales Operations & Deal Desk Case")
        selected_area = st.selectbox(
            "Choose Case Type",
            ["", "Deal Desk", "Sales Operations", "Billing", "Legal"],
            help="Pick a case category to proceed."
        )

        if selected_area:
            st.markdown(f"### ✍️ Provide details for your **{selected_area}** case")
            account = st.text_input("Account Name")
            opportunity = st.text_input("Opportunity")
            quote = st.text_input("Quote")
            contact = st.text_input("Contact Name")
            case_type = st.selectbox("Case Type", ["Quote", "Accounts", "Contacts"])
            case_sub_type = st.text_input("Case Sub-Type")

            if st.button("📩 Submit Case"):
                st.success("✅ Case submitted successfully!")
                st.write("### Case Summary:")
                st.write(f"- **Account Name**: {account}")
                st.write(f"- **Opportunity**: {opportunity}")
                st.write(f"- **Quote**: {quote}")
                st.write(f"- **Contact Name**: {contact}")
                st.write(f"- **Case Area**: {selected_area}")
                st.write(f"- **Case Type**: {case_type}")
                st.write(f"- **Case Sub-Type**: {case_sub_type}")
