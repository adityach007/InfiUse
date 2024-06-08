import streamlit as st
import os
import random
from datetime import datetime
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import json
import requests
from streamlit_ace import st_ace
import uuid
from blog import (load_blog_posts, save_blog_posts, create_blog_post, generate_code_for_blog, 
                  view_blog_posts, is_technical_topic, edit_blog_post, delete_blog_post)

from chat import chat, download_chat
from collab import code_snippets_sharing, view_code_snippets
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

groq_api_key = os.environ['GROQ_API_KEY']
api_key = os.environ['FIREWORKS_API_KEY']
API_KEY = os.environ["codestral_api"]

# The endpoint you want to hit
url = "https://codestral.mistral.ai/v1/chat/completions"

blog_posts_file = 'blog_posts.json'


def fetch_response(messages):
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
        "model": "accounts/fireworks/models/qwen2-72b-instruct",
        "max_tokens": 4096,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [{"role": "user", "content": messages}]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

def file_response(prompt, file_contents):
        # Log the inputs
        logger.info(f"Prompt: {prompt}")
        logger.info(f"File contents: {file_contents}")

        # Create the prompt for the conversation
        prompt = f"{prompt} {file_contents}"
        groq_chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="llama3-8b-8192")

        conversation = ConversationChain(
            llm=groq_chat,
            memory=ConversationBufferWindowMemory(k=5)
        )

        response = conversation(prompt)
        content = response['response']
        return content


def about():
    st.title("About")
    st.write('''
        
InfiUse Blog App leverages advanced technologies to enhance your blogging experience. From AI-powered code generation to collaborative editing tools, 
             it provides cutting-edge solutions to streamline your workflow. With its seamless integration of chatbots, you can interact with intelligent assistants to assist you in content creation and research. 
             Stay ahead of the curve with InfiUse's innovative features, designed to simplify the complexities of blogging in today's digital landscape.
    ''')

def inspect_and_run_code(code_content):
    prompt = f'''display the output of the following code:
                {code_content}
                '''

    response = fetch_response(prompt)


    return response['choices'][0]['message']['content']



def help():
    st.subheader("Currently working on this page...")


users_db_file = 'users_db.json'

# Function to load user data
def load_users():
    if os.path.exists(users_db_file):
        with open(users_db_file, 'r') as f:
            return json.load(f)
    else:
        return []

# Function to save user data
def save_users(users):
    with open(users_db_file, 'w') as f:
        json.dump(users, f)



# Function to authenticate a user
def authenticate_user(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user['user_key']
    return None


def find_user_by_username(username):
    users = load_users()
    for user in users:
        if user['username'] == username:
            return user
    return None

# Function to reset password
def reset_password(username, new_password):
    users = load_users()
    for user in users:
        if user['username'] == username:
            user['password'] = new_password
            save_users(users)
            return True
    return False

def help():
    st.title("Coding Help Forum")
    st.subheader("Constructing this page...")

    # # Display options for the user
    # options = st.radio("Select an Option:", ["Ask a Question", "Answer a Question"])

    # if options == "Ask a Question":
    #     # Ask a question
    #     question = st.text_input("Ask your coding question:")
    #     if st.button("Submit Question"):
    #         if question:
    #             st.success("Question submitted successfully!")
    #             # Store the question in a database or file

    # elif options == "Answer a Question":
    #     # Display existing questions and answers
    #     st.subheader("Existing Questions and Answers:")
    #     questions = {
    #         "How to sort a list in Python?": ["User1", "User2"],
    #         "How to implement a bubble sort algorithm?": ["User3"]
    #     }
    #     selected_question = st.selectbox("Select a Question:", list(questions.keys()))
    #     if selected_question:
    #         st.write(f"Question: {selected_question}")
    #         st.write("Asked by:")
    #         for user in questions[selected_question]:
    #             st.write(f"- {user}")

    #         # Provide an answer to the selected question
    #         new_answer = st.text_area("Your Answer:")
    #         if st.button("Submit Answer"):
    #             if new_answer:
    #                 st.write("- " + new_answer)
    #                 st.success("Answer submitted successfully!")
    #                 # Store the answer in a database or file
    #             else:
    #                 st.warning("Please enter your answer before submitting.")


# Function to manage user sessions
def login_interface():
        # Set the background image
    background_image = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
        background-image: url("https://e0.pxfuel.com/wallpapers/407/732/desktop-wallpaper-light-blue-gradient-21319-data-src-background-for-login-pastel-blue-gradient.jpg");
        background-size: cover;  # This ensures the image covers the entire background
        background-position: center;
        background-repeat: no-repeat;
    }
    </style>
    """

    st.markdown(background_image, unsafe_allow_html=True)


    st.title("User Authentication")

    menu = ["Login", "Register", "Forgot Password", "Admin"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":

        st.subheader("Login Section")

        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user_key = authenticate_user(username, password)
            if user_key:
                st.session_state['user_key'] = user_key
                st.session_state['username'] = username
                st.success(f"Welcome {username}")
                st.experimental_rerun()  # Rerun the app to update the state
            else:
                st.error("Invalid Username/Password")

    elif choice == "Register":
        st.subheader("Register Section")

        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')
        security_question = st.text_input("Security Question")
        security_answer = st.text_input("Security Answer", type='password')
        if st.button("Register"):
            register_user(new_user, new_password, security_question, security_answer)
            st.success("You have successfully created an account")
            st.info("Go to Login Menu to login")

    elif choice == "Forgot Password":
        st.subheader("Forgot Password Section")

        username = st.text_input("Enter your username")
        if st.button("Submit"):
            user = find_user_by_username(username)
            if user:
                st.session_state['reset_username'] = username
                st.session_state['security_question'] = user['security_question']
                st.experimental_rerun()

    if 'reset_username' in st.session_state:
        st.subheader("Reset Password Section")
        st.write(f"Security Question: {st.session_state['security_question']}")
        security_answer = st.text_input("Answer to security question", type='password')
        new_password = st.text_input("New Password", type='password')
        if st.button("Reset Password"):
            user = find_user_by_username(st.session_state['reset_username'])
            if user and user['security_answer'] == security_answer:
                reset_password(st.session_state['reset_username'], new_password)
                st.success("Password reset successfully")
                st.session_state.pop('reset_username')
                st.session_state.pop('security_question')
            else:
                st.error("Incorrect answer to security question")


def register_user(username, password, security_question, security_answer):
    users = load_users()
    user_key = str(uuid.uuid4())
    users.append({
        'username': username,
        'password': password,
        'user_key': user_key,
        'security_question': security_question,
        'security_answer': security_answer,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })
    save_users(users)



# Main function to run the app
def main():

    if 'user_key' not in st.session_state:
        login_interface()
    else:
        st.sidebar.title(f"Welcome {st.session_state['username']}")



        # Add customization options to the sidebar
        st.sidebar.title('Navigation')
        page = st.sidebar.selectbox("Go to", [
            "Select options",
            "Blog Creation",
            "Code Sharing and Collaboration",
            "Chat",
            "Logout"
        ])

        if page == "Select options":
            about()

        elif page == "Blog Creation":
            collaboration_page = st.sidebar.radio("Options", [
                "Blog Creation",
                "View Blog posts",
                "Edit Blogs",
                "Delete Blogs"
            ])

            if 'coins' not in st.session_state:
                st.session_state.coins = 0

            # Display coin meter at top-left corner of sidebar
            st.sidebar.markdown(f"💰 **Coins:** {st.session_state.coins}")

            if collaboration_page == "Blog Creation":
                create_blog_post()
            elif collaboration_page == "View Blog posts":
                view_blog_posts()
            elif collaboration_page == "Edit Blogs":
                edit_blog_post()
            elif collaboration_page == "Delete Blogs":
                delete_blog_post()


        elif page == "Code Sharing and Collaboration":
            collaboration_page = st.sidebar.radio("Options", [
                "Code Snippets Sharing",
                "Collaborative Coding",
                "Help"
            ])

            if collaboration_page == "Code Snippets Sharing":
                code_snippets_sharing()
            elif collaboration_page == "Collaborative Coding":
                view_code_snippets()
            elif collaboration_page == "Help":
                help()
        
        elif page == "Chat":
            chat()

        elif page == "Logout":
            st.session_state.pop('user_key')
            st.session_state.pop('username')
            st.success("You have successfully logged out")
            st.experimental_rerun()

if __name__ == '__main__':
    main()


