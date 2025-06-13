import streamlit as st
import requests
import json
import time
import threading

# Configure page
st.set_page_config(page_title="Salesforce Case Mock", layout="centered")

st.markdown("""
    <style>
    /* Make st.info() text white */
    .stAlert[data-testid="stAlert-info"] {
        background-color: #1b74e4;  /* Optional: deeper blue */
        color: white;
    }
    .stAlert[data-testid="stAlert-info"] p {
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Override st.info() background and text color */
    .stAlert[data-testid="stAlert-info"] {
        background-color: #1b74e4 !important;  /* Optional: darker blue background */
        color: white !important;
        border: none;
    }

    .stAlert[data-testid="stAlert-info"] p {
        color: white !important;
    }

    /* Ensure any inline spans or strong text are white too */
    .stAlert[data-testid="stAlert-info"] span,
    .stAlert[data-testid="stAlert-info"] strong {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Make all markdown links yellow */
    a {
        color: yellow !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Make all form field labels white */
    label {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# Centered and smaller "Restart" button
st.markdown(
    """
    <style>
    .small-button button {
        font-size: 14px !important;
        padding: 0.3em 1em;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.markdown(
    """
    <h1 style='text-align: center;'>📄 Sales Operations & Deal Desk Cases</h1>
    """,
    unsafe_allow_html=True
)

# 🎨 Add Salesforce Blue styling
st.markdown(
    """
    <style>
        .main {
            background-color: #0070d2;
        }
        .stApp {
            background-color: #0070d2;
            color: white;
        }
        .stTextArea textarea, .stSelectbox div, .stButton button {
            background-color: white;
            color: black;
        }
        h1, h2, h3, h4 {
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Session state initialization
if 'initialized' not in st.session_state:
    st.session_state.clear()
    st.session_state.initialized = True

if 'step' not in st.session_state:
    st.session_state.step = 1



# Step 1: User input
if st.session_state.step == 1:
    st.subheader("Kindly check with our AI Agent before opening a new Sales Operations or Deal Desk case.")
    user_input = st.text_area("", height=70)


    if st.button("Submit To Doti (Our AI)➡️"):
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
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={"query": user_input}
                    )
                    response.raise_for_status()
                    result_container['response'] = response.json()
                    result_container['success'] = True
                except Exception as e:
                    result_container['error'] = str(e)
                    result_container['success'] = False

            # Launch API call in a background thread
            request_thread = threading.Thread(target=make_request)
            request_thread.start()

            # Live seconds counter loop
            while request_thread.is_alive():
                elapsed = int(time.time() - start_time)
                
                placeholder.markdown(f"""
                 <div style="background-color: #1b74e4; padding: 1em; border-radius: 5px; color: white; text-align: center;">
                  ⏱️ Waiting for Doti to respond... {elapsed} seconds elapsed (it takes time for the API to reply...)
                  </div>
                """, unsafe_allow_html=True)


                time.sleep(1)

            # Clear counter display
            placeholder.empty()

            # Handle API result
            if result_container.get("success"):
                st.session_state.api_result = result_container["response"]
                st.session_state.response_time = time.time() - start_time
                st.session_state.step = 2
                st.info(
                    f"✅ Doti responded!\n\n"
                    f"⏱️ Total response time: {st.session_state.response_time:.2f} seconds"
                )
                st.rerun()
            else:
                st.error(f"API request failed: {result_container.get('error')}")
elif st.session_state.step == 2:
    st.subheader("🤖 Doti's Parsed Response")

    response_data = st.session_state.api_result
    question = response_data.get("question", "N/A")
    answer = response_data.get("answer", "N/A")
    sources = response_data.get("sources", [])

    st.markdown(f"### ❓ Question:\n{question}")
    st.markdown(f"### 🧠 Answer:\n{answer}")
    st.markdown("### 📚 Sources:")
    if sources:
        for idx, source in enumerate(sources, start=1):
            name = source.get("name", "Unnamed Source")
            link = source.get("link", "No link provided")
            relevancy = source.get("relevancy", "Unknown")
            st.markdown(f"""**{idx}. {name}**  
🔗 [View Source]({link})  
📊 Relevancy: {relevancy}
""")
    else:
        st.markdown("_No sources provided._")



    st.subheader("🏷️ If your answer was not resolved, please open a new case")

    # Use a TEMPORARY key to avoid conflicts
    selected_area = st.selectbox(
        "Select the relevant case area",
        ["Deal Desk", "Sales Operations", "Billing", "Legal"],
        key="temp_case_area"
    )

    if st.button("➡️ Continue to Case Details"):
        # Now store into actual session state variable AFTER widget is done
        st.session_state.case_area = selected_area
        st.session_state.step = 3
        st.rerun()

# Step 3: Case Details Entry
elif st.session_state.step == 3:
    st.subheader(f"📬 Submit New {st.session_state.case_area} Case")

    st.text_input("Account Name", key="account_name")
    st.text_input("Opportunity", key="opportunity")
    st.text_input("Quote", key="quote")
    st.text_input("Contact Name", key="contact_name")
    case_type = st.selectbox("Case Type", ["Quote", "Accounts", "Contacts"], key="case_type")
    case_sub_type = st.text_input("Case Sub-Type", key="case_sub_type")

    if st.button("📩 Submit New Case"):
        st.success("✅ New case submitted successfully!")
        st.write("**Case Summary:**")
        st.write(f"• **Account Name**: {st.session_state.account_name}")
        st.write(f"• **Opportunity**: {st.session_state.opportunity}")
        st.write(f"• **Quote**: {st.session_state.quote}")
        st.write(f"• **Contact Name**: {st.session_state.contact_name}")
        st.write(f"• **Case Area**: {st.session_state.case_area}")
        st.write(f"• **Case Type**: {st.session_state.case_type}")
        st.write(f"• **Case Sub-Type**: {st.session_state.case_sub_type}")

        # Reset flow
        if st.button("🏁 Start Over"):
            st.session_state.step = 1
            st.experimental_rerun()

cols = st.columns([1, 2, 1])  # Left, Center, Right
with cols[1]:
    with st.container():
        if st.button("🔄", key="restart_button"):
            st.session_state.clear()
            st.rerun()
