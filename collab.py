import streamlit as st
import os
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from streamlit_ace import st_ace
import uuid
import time
import PyPDF2
from docx import Document

load_dotenv()

groq_api_key = os.environ['GROQ_API_KEY']
api_key = os.environ['FIREWORKS_API_KEY']
API_KEY = os.environ["codestral_api"]

# The endpoint you want to hit
url = "https://codestral.mistral.ai/v1/chat/completions"


def extract_text_from_docx(docx_file):
    doc = Document(docx_file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def generate_code_title(code):
    prompt = f'''
        Generate only one good title for {code} 
    '''

    groq_chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")


    conversation = ConversationChain(
        llm=groq_chat,
        memory=ConversationBufferWindowMemory(k=5)
    )

    response = conversation(prompt)
    content = response['response']
    return content

def format_code(code_snippets, index, generated_titles):
    formatted_code_list = []

    for i, snippet in enumerate(code_snippets):
        # Extract language and code from the snippet dictionary
        language = snippet.get('language', '')
        code = snippet.get('code', '')

        # Split the code into lines
        lines = code.split('\n')

        # Initialize an empty string to store the formatted code
        formatted_code = ''

        # Define the indentation level
        indent_level = 0

        # Define the string to use for indentation (e.g., four spaces)
        indent_string = '    '

        # Loop through each line of code
        for line in lines:
            # Strip leading and trailing whitespace from the line
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check if the line ends with a colon (indicating the start of an indented block)
            if line.endswith(':'):
                # Add the line to the formatted code with proper indentation
                formatted_code += indent_string * indent_level + line + '\n'
                # Increase the indentation level for the next block
                indent_level += 1
            else:
                # Add the line to the formatted code with proper indentation
                formatted_code += indent_string * indent_level + line + '\n'

        formatted_code_list.append({'language': language, 'formatted_code': formatted_code})

    if index not in generated_titles:
        # If a title has not been generated for this index, generate it
        formatted_languages = [snippet['language'] for snippet in code_snippets]
        formatted_codes = [snippet['formatted_code'] for snippet in formatted_code_list]

        prompt = f'''
            Generate only one title for {formatted_codes[index]} which is in {formatted_languages[index]} language
            return the title in simple text format only and also 5-6 words maximum length of title.
        '''

        groq_chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")

        conversation = ConversationChain(
            llm=groq_chat,
            memory=ConversationBufferWindowMemory(k=5)
        )

        response = conversation(prompt)
        generated_titles[index] = response['response']

    # Use the generated title for the current code snippet
    formatted_titles = [generated_titles[index] for _ in code_snippets]

    return formatted_titles


def code_snippets_sharing():
    from app import file_response, inspect_and_run_code
    st.title("Upload Code, PDF, or DOCX File")

    conversational_memory_length = 5
    memory = ConversationBufferWindowMemory(k=conversational_memory_length)

    # Dictionary to store uploaded files and their contents
    if 'uploaded_files_dict' not in st.session_state:
        st.session_state.uploaded_files_dict = {}
    
    if 'file_chat_sessions' not in st.session_state:
        st.session_state.file_chat_sessions = {}

    if 'file_current_session_id' not in st.session_state:
        st.session_state.file_current_session_id = str(uuid.uuid4())
        st.session_state.file_chat_sessions[st.session_state.file_current_session_id] = []

    # Function to switch chat session
    def switch_chat_session(session_id):
        st.session_state.file_current_session_id = session_id

    # Dropdown to select chat session
    session_ids = list(st.session_state.file_chat_sessions.keys())
    selected_session_id = st.session_state.file_current_session_id  # Initialize selected_session_id to current_session_id
    if selected_session_id not in session_ids:
        session_ids.append(selected_session_id)
    
    selected_session_id = st.sidebar.selectbox("Select Chat Session", session_ids, index=session_ids.index(selected_session_id), on_change=switch_chat_session, args=(selected_session_id,))
    
    # Ensure current session ID is valid
    if st.session_state.file_current_session_id is None or st.session_state.file_current_session_id not in st.session_state.file_chat_sessions:
        if st.session_state.file_chat_sessions:
            st.session_state.file_current_session_id = next(iter(st.session_state.file_chat_sessions))
        else:
            st.session_state.file_current_session_id = str(uuid.uuid4())
            st.session_state.file_chat_sessions[st.session_state.file_current_session_id] = []

    current_chat_history = st.session_state.file_chat_sessions.get(st.session_state.file_current_session_id, [])

    for message in current_chat_history:
        memory.save_context({'input': message['human']}, {'output': message['AI']})

    # Allow user to upload multiple files via drag and drop
    uploaded_files = st.file_uploader(
        "Drag and drop code, PDF, or DOCX files here", 
        type=["py", "cpp", "java", "c", "html", "css", "javascript", "php", "swift", "rb", "go", "ts", "kt", "lua", "pl", "sh", "sql", "r", "rust", "dart", "scala", "groovy", "asm", "perl", "vb", "jsx", "tsx", "yaml", "json", "xml", "cs", "m", "hpp", "h", "hs", "coffee", "erl", "clj", "fs", "lisp", "elm", "v", "zig", "pug", "scss", "sass", "less", "ejs", "twig", "pdf", "docx"], 
        accept_multiple_files=True
    )
    
    # Process the uploaded files
    if uploaded_files is not None:
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.pdf'):
                # Extract text from PDF using PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = ""
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    pdf_text += page.extract_text()
                file_contents = pdf_text
            elif uploaded_file.name.endswith('.docx'):
                file_contents = extract_text_from_docx(uploaded_file)
            else:
                file_contents = uploaded_file.getvalue().decode("utf-8")
            
            # Update the dictionary with the new file contents
            st.session_state.uploaded_files_dict[uploaded_file.name] = file_contents
    
    # Dropdown to select uploaded file in the sidebar and show preview
    st.sidebar.title("Uploaded Files Preview")
    selected_file = st.sidebar.selectbox("Select Uploaded File", list(st.session_state.uploaded_files_dict.keys()))
    
    if selected_file:
        selected_file_content = st.session_state.uploaded_files_dict[selected_file]
        st.subheader(f"Preview of {selected_file}")
        if selected_file.split('.')[-1] in ["py", "cpp", "java", "c", "html", "css", "javascript", "php", "swift", "rb", "go", "ts", "kt", "lua", "pl", "sh", "sql", "r", "rust", "dart", "scala", "groovy", "asm", "perl", "vb", "jsx", "tsx", "yaml", "json", "xml", "cs", "m", "hpp", "h", "hs", "coffee", "erl", "clj", "fs", "lisp", "elm", "v", "zig", "pug", "scss", "sass", "less", "ejs", "twig"]:
            st_ace(
                value=selected_file_content,
                language="python",
                height=300,
                auto_update=True,
                keybinding="sublime",
                theme="monokai",
                font_size=14,
                show_gutter=True,
                show_print_margin=False,
                wrap=True,
                tab_size=4,
                key=f"preview_{selected_file}",
                readonly=True
            )
        else:
            st.text_area(
                label="",
                value=selected_file_content,
                height=300,
                key=f"preview_{selected_file}",
                disabled=True  # Disabling input for text area
            )

    st.subheader("Conversation History")

    for idx, message in enumerate(current_chat_history):
        with st.chat_message("user"):
            st.write(message['human'])
        with st.chat_message("assistant"):
            st.write(message["AI"])

    # Chat with AI about the uploaded files
    user_question = st.text_area("Ask a question:", key="file_user_question")
    if st.button("Chat about Uploaded Files"):
        user_question = st.session_state.file_user_question
        if user_question:
            # Measure the start time
            start_time = time.time()

            # Use AI to generate response
            response = file_response(user_question, list(st.session_state.uploaded_files_dict.values()))

            # Measure the end time
            end_time = time.time()

            # Calculate the elapsed time
            elapsed_time = end_time - start_time

            # Ensure response is a string
            response_text = response if isinstance(response, str) else str(response)

            message = {'human': user_question, 'AI': response_text, 'feedback': None, 'response_time': elapsed_time}
            current_chat_history.append(message)

            # Save current chat history back to session state
            st.session_state.file_chat_sessions[st.session_state.file_current_session_id] = current_chat_history
            
            st.experimental_rerun()


def view_code_snippets():
    from app import file_response, inspect_and_run_code
    st.title("View Code Snippets")
    
    # Layout for Messages and Output boxes
    col1, col2 = st.columns(2)

    # Messages Box (Left Column)
    with col1:
        st.subheader("Messages")
        user_question = st.text_area("Ask a question:", key="user_question")

        # Buttons for Clear and Submit
        col1_1, col1_2 = st.columns([1, 4])
        with col1_1:
            if st.button("Clear", key="clear_button"):
                st.session_state["user_question"] = ""
                user_question = ""
        with col1_2:
            if st.button("Submit", key="submit_button"):
                # Call fetch_response function to get response
                response = inspect_and_run_code(user_question)
                st.session_state["output"] = response

                # Show output immediately
                st.experimental_rerun()

    # Output Box (Right Column)
    with col2:
        st.subheader("Output")
        output_text = st.session_state.get("output", "")

        # Update the output text area with the returned response
        st.text_area(
            label="",
            value=output_text,
            height=300,
            key="output_text_area",
            disabled=True  # Disable input for the text area
        )

        if output_text:
            st.download_button(
                label="Download Output",
                data=output_text,
                file_name="output.txt",
                mime="text/plain"
            )



def download_output(output_text, language):
    # Determine the appropriate file extension based on the language
    if language.lower() == "python":
        ext = ".py"
    else:
        ext = ".txt"  # Default extension

    # Create the file name using the determined extension
    file_name = f"output{ext}"

    # Write the output text to the file
    with open(file_name, "w") as f:
        f.write(output_text)

    # Provide a download button for the user
    st.download_button(label="Download Output", data=output_text, file_name=file_name)
