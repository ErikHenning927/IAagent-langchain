import streamlit as st
from langchain_openai import ChatOpenAI
from agent import *
from databases import *
from process_message import process_message 

process_message = process_message

class ChatLLM:
    def __init__(self, model="gpt-4-turbo"):
        self.llm = ChatOpenAI(model=model)
        self.chat_history = []
        self.dataframes = load_all_tables_from_db()
        create_agent(self)
    process_message = process_message  # atribui a função importada como método da classe
    
    def get_response(self, user_input):
        response = self.process_message(user_input)
        self.chat_history.append((user_input, response))
        return response
   
# Streamlit App
st.set_page_config(page_title="Powder AI", page_icon="🤖")
st.title("🤖 Powder AI")

if "chat" not in st.session_state:
    st.session_state.chat = ChatLLM()

def send_message():
    user_input = st.session_state.user_input
    if user_input:
        response = st.session_state.chat.get_response(user_input)
        st.session_state.chat.chat_history.append((user_input, response))
        st.session_state.user_input = ""  # limpa input

# Text input com Enter
st.text_input("Digite sua pergunta:", key="user_input", on_change=send_message)

# Exibe histórico
if st.session_state.chat.chat_history:
    st.write("---")
    st.subheader("Histórico")
    for q, a in st.session_state.chat.chat_history:
        st.write(f"**Você:** {q}")
        st.write(f"**Powder:** {a}")