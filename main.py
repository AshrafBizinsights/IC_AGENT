from crew import ICAgents
from dotenv import load_dotenv
import streamlit as st
import os
import pandas as pd

# Load environment variables
load_dotenv()

# Delete previous Excel output if exists
output_path = 'output/calculated_goals.xlsx'
if os.path.exists(output_path):
    os.remove(output_path)

# Set API keys
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_API_KEY", "your-key-here")
os.environ["MODEL"] = os.getenv("MODEL", "claude-3-sonnet-20240229")

# Streamlit page config
st.set_page_config(page_title="ICAgents Goal Calculator", layout="centered")

# Header
st.markdown("""
    <h2 style='text-align: center; margin-bottom: 0.5rem;'>🤖 ICAgents - Goal Calculation Chatbot</h2>
    <p style='text-align: center; font-size: 1.1rem; color: gray;'>A multi-agent assistant to calculate your goals dynamically</p>
""", unsafe_allow_html=True)

# Session state init
if "messages" not in st.session_state:
    st.session_state.messages = []
if "awaiting_bot" not in st.session_state:
    st.session_state.awaiting_bot = False
if "latest_user_input" not in st.session_state:
    st.session_state.latest_user_input = ""

# CSS for layout
st.markdown("""
<style>
    .chat-container {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-bottom: 160px;
    }
    .user-msg, .bot-msg {
        margin: 0.5rem 0;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        max-width: 80%;
        word-wrap: break-word;
        display: flex;
        align-items: center;
    }
    .user-msg {
        background-color: #1e1e1e;
        color: white;
        align-self: flex-end;
        margin-left: auto;
    }
    .bot-msg {
        background-color: #fff8dc;
        color: black;
        align-self: flex-start;
    }
    .icon {
        width: 30px;
        height: 30px;
        margin-right: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .user-icon {
        background-color: #dc3545;
        border-radius: 50%;
        font-weight: bold;
        color: white;
    }
    .bot-icon {
        background-color: #ffc107;
        border-radius: 50%;
        font-weight: bold;
        color: black;
    }
    .input-container {
        position: fixed;
        bottom: 1rem;
        left: 0;
        width: 100%;
        background-color: #0e1117;
        padding: 1rem 2rem;
        box-shadow: 0 -1px 8px rgba(0,0,0,0.4);
        z-index: 999;
    }
    .rounded-input input {
        border-radius: 2rem;
        border: 1px solid #dc3545;
        padding: 0.75rem 1rem;
        width: 100%;
        background-color: #1e1e1e;
        color: white;
    }
    .block-container {
        padding-bottom: 180px !important;
    }
</style>
""", unsafe_allow_html=True)

# Display chat history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for i, (sender, message) in enumerate(st.session_state.messages):
    if sender == "bot" and "last_bot_response" in st.session_state and message == st.session_state.last_bot_response:
        continue
    role_class = "user-msg" if sender == "user" else "bot-msg"
    icon = "🙎‍♂️" if sender == "user" else "🧠"
    icon_class = "user-icon" if sender == "user" else "bot-icon"
    st.markdown(f"""
        <div class="{role_class}">
            <div class="icon {icon_class}">{icon}</div>
            {message}
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Show final result box
if "last_bot_response" in st.session_state and not st.session_state.awaiting_bot:
    st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; border-radius: 0.5rem;">
            <h4 style="color: hotpink; display: flex; align-items: center;">
                🧠 <span style="margin-left: 0.5rem;">Result</span>
            </h4>
    """, unsafe_allow_html=True)

    st.markdown(
        f"""<div style="background-color: #0b3558; color: #e0f4ff; padding: 1.2rem; border-radius: 10px;">
        {str(st.session_state.last_bot_response).replace("\n", "<br>")}
        </div>""",
        unsafe_allow_html=True
    )

    if st.session_state.get("excel_available", False) and os.path.exists(st.session_state.get("excel_path", "")):
        with open(st.session_state.excel_path, "rb") as f:
            df = pd.read_excel(f)
            st.dataframe(df)
            st.download_button(
                label="⬇️ Download Excel File",
                data=f,
                file_name="calculated_goals.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    st.markdown("</div>", unsafe_allow_html=True)

# Input form
with st.form("chat_form", clear_on_submit=True):
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    user_input = st.text_input("", placeholder="Ask your question here...", label_visibility="collapsed", key="user_text")
    submitted = st.form_submit_button("➤")
    st.markdown('</div>', unsafe_allow_html=True)

# On user input
if submitted and user_input:
    for key in ["last_bot_response", "excel_available", "excel_path"]:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.messages.append(("user", user_input))
    st.session_state.latest_user_input = user_input
    st.session_state.awaiting_bot = True
    st.rerun()

# Bot response logic
if st.session_state.awaiting_bot:
    with st.spinner("Thinking..."):
        try:
            crew = ICAgents()
            user_agent = crew.input_crew()

            # Run agent without passing memory manually
            result = user_agent.kickoff(inputs={ "user_input": user_input })

            if isinstance(result, str):
                st.session_state.last_bot_response = result
            elif isinstance(result, dict):
                st.session_state.last_bot_response = result.get("response", "Okay!")

                # Optional: Check memory for triggering crew
                quarter = result.get("quarter")
                national_goal = result.get("national_goal")

                if quarter and national_goal:
                    st.success("✅ Info complete. Running calculation...")
                    full_crew = crew.calculation_crew()
                    result = full_crew.kickoff(inputs={
                        "quarter": quarter,
                        "national_goal": national_goal
                    })
                    st.session_state.last_bot_response = result

                    # Excel handling
                    excel_path = "output/calculated_goals.xlsx"
                    if os.path.exists(excel_path):
                        st.session_state.excel_available = True
                        st.session_state.excel_path = excel_path
                    else:
                        st.session_state.excel_available = False
                else:
                    st.session_state.excel_available = False
            else:
                st.session_state.last_bot_response = str(result)

        except Exception as e:
            print("ERROR:", e)
            st.session_state.last_bot_response = "❌ Something went wrong."
            st.session_state.excel_available = False

        st.session_state.messages.append(("bot", st.session_state.last_bot_response))
        st.session_state.awaiting_bot = False
        st.session_state.latest_user_input = ""
        st.rerun()
