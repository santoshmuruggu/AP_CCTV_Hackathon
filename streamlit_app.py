# streamlit_app.py

import streamlit as st
from query_agent import ask_sql_agent

st.set_page_config(page_title="🧠 CCTV DB Chatbot", layout="centered")

st.title("📹 AI-Powered CCTV Database Chatbot")
st.markdown("Ask questions like:")
st.markdown("""
- *Show 5 latest unauthorized vehicle logs*  
- *How many bags were moved on 2025-05-08?*  
- *Who entered the warehouse yesterday?*
""")

# Session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_query = st.text_input("💬 Ask a question to your warehouse database:", key="query_input")

if user_query:
    with st.spinner("Thinking... 🤖"):
        answer = ask_sql_agent(user_query)
        st.session_state.chat_history.append((user_query, answer))

# Display chat history
st.markdown("---")
for query, response in reversed(st.session_state.chat_history):
    st.markdown(f"**🧑‍💻 You:** {query}")
    st.markdown(f"**🤖 GPT:** {response}")
    st.markdown("---")
