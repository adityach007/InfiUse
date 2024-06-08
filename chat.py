import streamlit as st
import os
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import base64
import requests
import uuid
import time

load_dotenv()
groq_api_key = os.environ['GROQ_API_KEY']

def download_chat(chat_history):
    chat_text = ""
    for message in chat_history:
        chat_text += f"User: {message['human']}\n"
        chat_text += f"AI: {message['AI']}\n\n"
    
    return chat_text

def chat():
    st.title("InfiUse Chat App")

    # Add customization options to the sidebar
    st.sidebar.title('Select an LLM')
    model = st.sidebar.selectbox('Choose a model', ['mixtral-8x7b-32768', 'llama3-8b-8192'])
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value=5)

    memory = ConversationBufferWindowMemory(k=conversational_memory_length)

    st.markdown("*Generally use Mistral model for code and Llama-3 for text related purposes*")

    # Initialize session state variables for chat sessions if not already initialized
    if 'chat_sessions' not in st.session_state:
        st.session_state.chat_sessions = {}

    if 'chat_current_session_id' not in st.session_state:
        st.session_state.chat_current_session_id = str(uuid.uuid4())
        st.session_state.chat_sessions[st.session_state.chat_current_session_id] = []

    # Function to switch chat session
    def switch_chat_session(session_id):
        st.session_state.chat_current_session_id = session_id

    # Dropdown to select chat session
    session_ids = list(st.session_state.chat_sessions.keys())
    selected_session_id = st.session_state.chat_current_session_id  # Initialize selected_session_id to current_session_id
    if selected_session_id not in session_ids:
        session_ids.append(selected_session_id)  # Add current_session_id to session_ids if not present

    selected_session_id = st.sidebar.selectbox("Select Chat Session", session_ids, index=session_ids.index(selected_session_id), on_change=switch_chat_session, args=(selected_session_id,))

    # Ensure current session ID is valid
    if st.session_state.chat_current_session_id is None or st.session_state.chat_current_session_id not in st.session_state.chat_sessions:
        if st.session_state.chat_sessions:
            st.session_state.chat_current_session_id = next(iter(st.session_state.chat_sessions))
        else:
            st.session_state.chat_current_session_id = str(uuid.uuid4())
            st.session_state.chat_sessions[st.session_state.chat_current_session_id] = []

    current_chat_history = st.session_state.chat_sessions.get(st.session_state.chat_current_session_id, [])

    for message in current_chat_history:
        memory.save_context({'input': message['human']}, {'output': message['AI']})

    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
        groq_api_key=groq_api_key,
        model_name=model
    )

    conversation = ConversationChain(
        llm=groq_chat,
        memory=memory
    )

    # Display conversation history in the main container
    st.subheader("Conversation History")

    for idx, message in enumerate(current_chat_history):

        with st.chat_message("user"):
            st.write(message['human'])
        
        with st.chat_message("assistant"):
            st.write(message["AI"])

    # Scroll to the bottom of the page after output is generated
    st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

    # User question text area covering full page width
    user_question = st.text_area("Ask a question:", key="chat_user_question")

    if st.button("Submit"):
        user_question = st.session_state.chat_user_question
        if user_question:
            # Measure the start time
            start_time = time.time()

            # Use Groq AI to generate response
            response = conversation(user_question)

            # Measure the end time
            end_time = time.time()

            # Calculate the elapsed time
            elapsed_time = end_time - start_time

            message = {'human': user_question, 'AI': response['response'], 'feedback': None, 'response_time': elapsed_time}
            current_chat_history.append(message)

            # Save current chat history back to session state
            st.session_state.chat_sessions[st.session_state.chat_current_session_id] = current_chat_history
            
            st.experimental_rerun()
    
    # Add download button to download chat history
    chat_text = download_chat(current_chat_history)
    st.download_button("Download Chat", chat_text, "chat_history.txt")