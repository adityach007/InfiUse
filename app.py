import streamlit as st
import os
from groq import Groq
import random
from datetime import datetime
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json
import base64
import requests
from streamlit_ace import st_ace
import uuid
import time


load_dotenv()

groq_api_key = os.environ['GROQ_API_KEY']
blog_posts_file = 'blog_posts.json'

# Replace with your actual API key
API_KEY = os.environ["codestral_api"]

# The endpoint you want to hit
url = "https://codestral.mistral.ai/v1/chat/completions"

def load_blog_posts():
    if os.path.exists(blog_posts_file):
        with open(blog_posts_file, 'r') as f:
            return json.load(f)
    else:
        return []

def save_blog_posts(blog_posts):
    with open(blog_posts_file, 'w') as f:
        json.dump(blog_posts, f)

def create_blog_post():


    st.title("Create a Blog Post")
    title = st.text_input("Title", placeholder="Do not use short-forms in the title")

    # Keywords input
    keywords = st.text_input("Keywords", placeholder="comma-separated")

    # erite the blog by yourself
    blog = st.text_area("Blog", placeholder="Write your blog...")

    # Range of the blog size
    numOfWords = st.slider("Number of words", min_value=250, max_value=2000, step=150)

    col1, col2 = st.columns(2)

    with col1:
        prompt = f'''
            Generate a comprehensive, engaging blog post relevant to the given title \"{title}\" and keywords \"{keywords}\". Make sure to incorporate these keywords in the blog post.
            The blog should be approximately {numOfWords} words in length, suitable for an online audience. Ensure the content is original, informative, and maintains a consistent tone throughout.
            Divide the blog into parts and provide some bullet points in each part.
        '''

        st.sidebar.title("Select the LLM")
        model = st.sidebar.selectbox(
            'Choose a model',
            ['mixtral-8x7b-32768', 'llama3-8b-8192', 'gemma-7b-it']
        )
        if st.button("Generate Content"):
            # Initialize Groq Langchain chat object and conversation
            groq_chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name=model)

            conversation = ConversationChain(
                llm=groq_chat,
                memory=ConversationBufferWindowMemory(k=5)
            )

            response = conversation(prompt)
            content = response['response']

            blog_post = {
                "title": title,
                "content": content,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            blog_posts = load_blog_posts()
            blog_posts.append(blog_post)
            save_blog_posts(blog_posts)
            st.success("Blog post created successfully.")
            
            # Increment coins and update session state
            st.session_state.coins += 5

    with col2:
            if st.button("Submit"):
                blog_post = {
                "title": title,
                "content": blog,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                blog_posts = load_blog_posts()
                blog_posts.append(blog_post)
                save_blog_posts(blog_posts)
                st.success("Blog post created successfully.")
                
                # Increment coins and update session state
                st.session_state.coins += 15    


def generate_code_for_blog(title, language):
    prompt = f"Generate a code for {title} in {language}"

    data = {
        "model": "codestral-latest",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error("Failed to get code completion. Please try again later.")
        return None

def view_blog_posts():
    st.title("Blog Posts")
    blog_posts = load_blog_posts()
    for i, blog_post in enumerate(blog_posts):
        with st.container(border=10):
            st.subheader(blog_post["title"])
            st.write(blog_post["content"])
            st.write(f"Created at: {blog_post['created_at']}")
            if is_technical_topic(blog_post["title"]):
                # Check if the current blog post is a technical topic
                button_key = f"generate_code_{i}"
                if st.button(f"Generate Code for {blog_post['title']}", key=button_key):
                    code = generate_code_for_blog(blog_post["title"], language='python')
                    if code:
                        st.code(code, language='python')
            st.write("---")




def is_technical_topic(topic):
    technical_keywords = ["AI", "machine learning", "data science", "programming", "technology", "software", "hardware", "coding", "computer science", "engineering", "artificial intelligence", "deep learning", "neural networks", "natural language processing", 
                        "computer vision", "big data", "cloud computing", "cybersecurity", "robotics", "internet of things", "IoT", "blockchain", "cryptocurrency", "virtual reality", "augmented reality", "3D printing", "quantum computing", "biotechnology", 
                        "genetic engineering", "bioinformatics", "nanotechnology", "renewable energy", "solar energy", "wind energy", "electric vehicles", "autonomous vehicles", "drone technology", "5G technology", "edge computing", "devops", "software development", 
                        "mobile app development", "web development", "game development", "digital marketing", "SEO", "social media algorithms", "network security", "ethical hacking", "penetration testing", "encryption", "data privacy", "GDPR", "cloud storage", 
                        "cloud security", "serverless computing", "microservices", "containerization", "Docker", "Kubernetes", "API development", "RESTful services", "graph databases", "SQL", "NoSQL", "database management", "data warehousing", "ETL processes", 
                        "business intelligence", "data analytics", "data visualization", "Power BI", "Tableau", "R programming", "Python programming", "Java programming", "C++ programming", "JavaScript programming", "TypeScript programming", "React", "Angular", 
                        "Vue.js", "Node.js", "Express.js", "Django", "Flask", "Spring Boot", "Ruby on Rails", "PHP", "Laravel", "Symfony", "ASP.NET", "C# programming", "Swift programming", "Kotlin programming", "Objective-C programming", "Scala programming", 
                        "Go programming", "Rust programming", "Perl programming", "Shell scripting", "Bash scripting", "PowerShell scripting", "TensorFlow", "PyTorch", "Keras", "OpenCV", "NLP libraries", "spaCy", "NLTK", "Hugging Face", "AWS", "Azure", 
                        "Google Cloud Platform", "IBM Cloud", "Alibaba Cloud", "Salesforce", "Oracle Cloud", "SAP", "Microsoft Dynamics", "Tableau", "Power BI", "QlikView", "Looker", "DataRobot", "H2O.ai", "RapidMiner", "Alteryx", "SAS", "SPSS", "MATLAB", 
                        "Simulink", "LabVIEW", "SolidWorks", "AutoCAD", "SketchUp", "Fusion 360", "CATIA", "ANSYS", "Comsol Multiphysics", "MATLAB", "R", "Python", "Julia", "Apache Hadoop", "Apache Spark", "Kafka", "Flink", "Beam", "Pig", "Hive", "HBase", 
                        "Cassandra", "MongoDB", "CouchDB", "Neo4j", "Redis", "Elasticsearch", "Logstash", "Kibana", "Apache NiFi", "Apache Airflow", "Apache Oozie", "Jenkins", "CircleCI", "Travis CI", "GitLab CI", "Bamboo", "Terraform", "Ansible", "Puppet", 
                        "Chef", "SaltStack", "CloudFormation", "Vagrant", "Nagios", "Zabbix", "Prometheus", "Grafana", "Splunk", "Datadog", "New Relic", "AppDynamics", "Raygun", "Sentry", "PagerDuty", "OpsGenie", "VictorOps", "ServiceNow", "JIRA", "Confluence", 
                        "Trello", "Asana", "Slack", "Microsoft Teams", "Zoom", "WebEx", "Google Meet", "Skype", "BlueJeans", "GoToMeeting", "BigBlueButton", "Moodle", "Blackboard", "Canvas", "Edmodo", "Schoology", "Brightspace", "Coursera", "Udacity", "edX", 
                        "Khan Academy", "Udemy", "LinkedIn Learning", "Pluralsight", "Cloud Academy", "A Cloud Guru", "Linux Academy", "ITProTV", "Cybrary", "SANS", "Cisco Networking Academy", "Oracle University", "Red Hat Training", "CompTIA", "Microsoft Learning", 
                        "IBM Training", "Google Cloud Training", "AWS Training", "Salesforce Training", "SAP Training", "Adobe Training", "Unity Training", "Unreal Engine Training", "GameMaker Studio", "Godot Engine", "CryEngine", "Lumberyard", "Frostbite", "Cocos2d", 
                        "Corona", "Defold", "Amazon Sumerian", "Blender", "Maya", "3ds Max", "Houdini", "ZBrush", "Substance Painter", "Quixel", "Marmoset Toolbag", "Sketchfab", "Unity", "Unreal Engine", "Godot", "CryEngine", "Lumberyard", "Blender", "Maya", 
                        "3ds Max", "Houdini", "ZBrush", "Cinema 4D", "Substance Painter", "Quixel", "Marmoset Toolbag", "Sketchfab", "Pixologic", "Mudbox", "Fusion 360", "SolidWorks", "AutoCAD", "Inventor", "CATIA", "Creo", "NX", "Revit", "Archicad", "Vectorworks", 
                        "Rhinoceros", "SketchUp", "Chief Architect", "Lumion", "V-Ray", "Corona Renderer", "Arnold", "Octane Render", "Redshift", "KeyShot", "Marmoset Toolbag", "Substance Designer", "Substance Alchemist", "Substance Source", "Quixel Megascans", 
                        "Allegorithmic", "Adobe XD", "Sketch", "Figma", "InVision", "Axure RP", "Balsamiq", "Marvel", "Framer", "ProtoPie", "Origami Studio", "Principle", "Flinto", "Adobe After Effects", "Adobe Premiere Pro", "Final Cut Pro", "Avid Media Composer", 
                        "DaVinci Resolve", "Sony Vegas Pro", "HitFilm", "Camtasia", "ScreenFlow", "iMovie", "Windows Movie Maker", "Blender", "Cinema 4D", "Maya", "3ds Max", "Houdini", "Nuke", "Fusion", "Blackmagic Design", "Red Giant", "Trapcode Suite", "Sapphire", 
                        "Boris FX", "Mocha Pro", "Silhouette", "Autodesk Flame", "Smoke", "Lustre", "Inferno", "Lustre", "Burn", "Blender", "Modo", "ZBrush", "Mudbox", "Marvelous Designer", "CLO 3D", "Substance Painter", "Substance Designer", "Quixel Mixer", "Houdini", 
                        "Cinema 4D", "Maya", "3ds Max", "Arnold", "V-Ray", "Redshift", "Octane Render", "KeyShot", "Marmoset Toolbag", "Blender", "Unity", "Unreal Engine", "Godot", "CryEngine", "Lumberyard", "Blender", "Maya", "3ds Max", "Houdini", "ZBrush", "Cinema 4D", 
                        "Substance Painter", "Quixel", "Marmoset Toolbag", "Sketchfab", "Pixologic", "Mudbox", "Fusion 360", "SolidWorks", "AutoCAD", "Inventor", "CATIA"]
    
    return any(keyword.lower() in topic.lower() for keyword in technical_keywords)


def edit_blog_post():
    st.title("Edit a Blog Post")
    blog_posts = load_blog_posts()
    if not blog_posts:
        st.write("No blog posts available to edit.")
        return
    
    post_titles = [post["title"] for post in blog_posts]
    selected_post = st.selectbox("Select a post to edit", post_titles)
    post = next((post for post in blog_posts if post["title"] == selected_post), None)
    
    if post:
        title = st.text_input("Title", post["title"])
        content = st.text_area("Content", post["content"])
        
        if st.button("Save Changes"):
            post["title"] = title
            post["content"] = content
            save_blog_posts(blog_posts)
            st.success("Blog post updated successfully.")

def delete_blog_post():
    st.title("Delete a Blog Post")
    blog_posts = load_blog_posts()
    if not blog_posts:
        st.write("No blog posts available to delete.")
        return
    
    post_titles = [post["title"] for post in blog_posts]
    selected_post = st.selectbox("Select a post to delete", post_titles)
    
    if st.button("Delete Post"):
        blog_posts = [post for post in blog_posts if post["title"] != selected_post]
        save_blog_posts(blog_posts)
        st.success("Blog post deleted successfully.")

def about():
    st.title("About")
    st.write('''
        
InfiUse Blog App leverages advanced technologies to enhance your blogging experience. From AI-powered code generation to collaborative editing tools, 
             it provides cutting-edge solutions to streamline your workflow. With its seamless integration of chatbots, you can interact with intelligent assistants to assist you in content creation and research. 
             Stay ahead of the curve with InfiUse's innovative features, designed to simplify the complexities of blogging in today's digital landscape.
    ''')

import streamlit as st
import requests
import json


def inspect_and_run_code(code_content, language):
    prompt = f'''display the output of the following code:
                {code_content} which is written in {language}. 
                Analyze the code for syntax and semantic errors.
                If any errors are found, suggest corrections.
                '''

    if language == "PHP":
        # Use Groq for PHP code analysis
        groq_chat = ChatGroq(temperature=0, groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")
        conversation = ConversationChain(llm=groq_chat, memory=ConversationBufferWindowMemory(k=5))
        response = conversation(prompt)
        content = response['response']
        return content, 50  # Return 50 points for successful PHP execution

    # For other languages, use Codestral API
    data = {
        "model": "codestral-latest",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Send the request to the Codestral API
    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error("Failed to get code completion. Please try again later.")
        return None  # Return 0 points for failed execution


def code_snippets_sharing():
    st.title("Code Snippets Sharing")

    # Language selection dropdown
    selected_language = st.selectbox("Select Language", ["Python", "Java", "C++", "JavaScript", "Ruby", "Swift", "PHP"])
    

    if selected_language == "Python":
        EXAMPLE_CODE = '''
        def greet(name):
            print(f"Hello, {name}!")

        def main():
            name = input("Enter your name: ")
            greet(name)

            for i in range(3):
                print(f"Iteration {i + 1}")

            print("Goodbye!")

        if __name__ == "__main__":
            main()
                '''
        
    elif selected_language == "Java":
        EXAMPLE_CODE = '''
        import java.util.Scanner;

        public class Main {
            public static void greet(String name) {
                System.out.println("Hello, " + name + "!");
            }

            public static void main(String[] args) {
                Scanner scanner = new Scanner(System.in);
                System.out.print("Enter your name: ");
                String name = scanner.nextLine();
                greet(name);

                for (int i = 0; i < 3; i++) {
                    System.out.println("Iteration " + (i + 1));
                }

                System.out.println("Goodbye!");
                scanner.close();
            }
        }
                '''
        
    elif selected_language == "C++":
        EXAMPLE_CODE = '''
        #include <iostream>
        #include <string>

        void greet(const std::string& name) {
            std::cout << "Hello, " << name << "!" << std::endl;
        }

        int main() {
            std::string name;
            std::cout << "Enter your name: ";
            std::getline(std::cin, name);
            greet(name);

            for (int i = 0; i < 3; i++) {
                std::cout << "Iteration " << (i + 1) << std::endl;
            }

            std::cout << "Goodbye!" << std::endl;
            return 0;
        }
                '''
        
    elif selected_language == "JavaScript":
        EXAMPLE_CODE = '''
        function greet(name) {
            console.log(`Hello, ${name}!`);
        }

        function main() {
            const name = prompt("Enter your name: ");
            greet(name);

            for (let i = 0; i < 3; i++) {
                console.log(`Iteration ${i + 1}`);
            }

            console.log("Goodbye!");
        }

        main();
                '''
        
    elif selected_language == "C#":
        EXAMPLE_CODE = '''
        using System;

        class Program {
            static void Greet(string name) {
                Console.WriteLine($"Hello, {name}!");
            }

            static void Main() {
                Console.Write("Enter your name: ");
                string name = Console.ReadLine();
                Greet(name);

                for (int i = 0; i < 3; i++) {
                    Console.WriteLine($"Iteration {i + 1}");
                }

                Console.WriteLine("Goodbye!");
            }
        }
                '''
        
    elif selected_language == "Ruby":
        EXAMPLE_CODE = '''
        def greet(name)
            puts "Hello, #{name}!"
        end

        def main
            print "Enter your name: "
            name = gets.chomp
            greet(name)

            3.times do |i|
                puts "Iteration #{i + 1}"
            end

            puts "Goodbye!"
        end

        main
                '''
        
    elif selected_language == "Swift":
        EXAMPLE_CODE = '''
        func greet(name: String) {
            print("Hello, \\(name)!")
        }

        func main() {
            print("Enter your name: ", terminator: "")
            if let name = readLine() {
                greet(name: name)
            }

            for i in 0..<3 {
                print("Iteration \\(i + 1)")
            }

            print("Goodbye!")
        }

        main()
                '''
        
    elif selected_language == "Go":
        EXAMPLE_CODE = '''
        package main

        import (
            "bufio"
            "fmt"
            "os"
        )

        func greet(name string) {
            fmt.Printf("Hello, %s!\\n", name)
        }

        func main() {
            reader := bufio.NewReader(os.Stdin)
            fmt.Print("Enter your name: ")
            name, _ := reader.ReadString('\\n')
            name = name[:len(name)-1] // remove newline character
            greet(name)

            for i := 0; i < 3; i++ {
                fmt.Printf("Iteration %d\\n", i+1)
            }

            fmt.Println("Goodbye!")
        }
                '''
        
    elif selected_language == "PHP":
        EXAMPLE_CODE = '''
        <?php
        function greet($name) {
            echo "Hello, $name!\\n";
        }

        function main() {
            echo "Enter your name: ";
            $name = trim(fgets(STDIN));
            greet($name);

            for ($i = 0; $i < 3; $i++) {
                echo "Iteration " . ($i + 1) . "\\n";
            }

            echo "Goodbye!\\n";
        }

        main();
        ?>
        '''

    # Text area for code input
    code_editor = st.text_area("Take base code and edit in Collaborative Coding...", value=EXAMPLE_CODE, height=200, disabled=True)

    # Button to save the code snippet
    if st.button("Save Code Snippet"):
        code_snippet = code_editor.strip()

        if code_snippet:
            # Save the code snippet to a file or database

            save_code_snippet(code_snippet, selected_language)
            st.success("Code snippet saved successfully.")
        else:
            st.warning("Please write some code before saving.")

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



def view_code_snippets():
    st.title("View Code Snippets")
    code_snippets_file = 'code_snippets.json'
    if os.path.exists(code_snippets_file):
        with open(code_snippets_file, 'r') as f:
            code_snippets = json.load(f)
        

    
        generated_titles = {}

        # Call the format_code function for each snippet
        for index, snippet in enumerate(code_snippets):
            formatted_titles = format_code(code_snippets, index, generated_titles)
            st.title(formatted_titles[index])

            # Button container
            col1, col2 = st.columns(2)

            # Run button
            with col1:
                run_button_key = f"run_button_{snippet['language'].lower()}_{index}"
                if st.button("Run Code", key=run_button_key):
                    result = inspect_and_run_code(snippet['code'], snippet['language'])
                    st.write(result)

            # Delete button
            with col2:
                delete_button_key = f"delete_button_{snippet['language'].lower()}_{index}"
                if st.button(f"Delete {snippet['language']} Code", key=delete_button_key):
                    delete_code_snippet(index)
                    st.success(f"{snippet['language']} code snippet deleted successfully.")

            # Edit button
            edited_code_key = f"edited_code_{snippet['language'].lower()}_{index}"
            edited_code = st_ace(
                value=snippet['code'],
                language=snippet['language'].lower(),
                height=300,
                auto_update=True,
                keybinding="sublime",
                theme="monokai",
                font_size=14,
                show_gutter=True,
                show_print_margin=False,
                wrap=True,
                tab_size=4,
                key=edited_code_key,
            )
            save_button_key = f"save_button_{snippet['language'].lower()}_{index}"
            if st.button(f"Save Changes for {snippet['language']}", key=save_button_key):
                save_edited_code_snippet(edited_code, snippet['language'], index)
                st.success(f"Changes for {snippet['language']} saved successfully.")

def delete_code_snippet(index):
    # Load existing code snippets from the JSON file
    code_snippets_file = 'code_snippets.json'
    if os.path.exists(code_snippets_file):
        with open(code_snippets_file, 'r') as f:
            code_snippets = json.load(f)
    else:
        code_snippets = []

    # Remove the code snippet at the specified index
    if 0 <= index < len(code_snippets):
        del code_snippets[index]

        # Save the updated list of code snippets back to the JSON file
        with open(code_snippets_file, 'w') as f:
            json.dump(code_snippets, f)

def save_code_snippet(code_snippet, language):
    # Load existing code snippets from the JSON file
    code_snippets_file = 'code_snippets.json'
    if os.path.exists(code_snippets_file):
        with open(code_snippets_file, 'r') as f:
            code_snippets = json.load(f)
    else:
        code_snippets = []

    # Add the new code snippet to the list
    new_code_snippet = {
        "language": language,
        "code": code_snippet,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    code_snippets.append(new_code_snippet)

    # Save the updated list of code snippets back to the JSON file
    with open(code_snippets_file, 'w') as f:
        json.dump(code_snippets, f)

def save_edited_code_snippet(code_snippet, language, index):
    # Load existing code snippets from the JSON file
    code_snippets_file = 'code_snippets.json'
    if os.path.exists(code_snippets_file):
        with open(code_snippets_file, 'r') as f:
            code_snippets = json.load(f)
    else:
        code_snippets = []

    # Update the code snippet with the edited code
    code_snippets[index]['code'] = code_snippet

    # Save the updated list of code snippets back to the JSON file
    with open(code_snippets_file, 'w') as f:
        json.dump(code_snippets, f)



def youtube_video_link_generator(human, ai):
    prompt = f"Suggest only youtube videos for {human} and {ai} and provide their links also."

    data = {
        "model": "codestral-latest",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        st.error("Failed to get code completion. Please try again later.")
        return None



def chat():
    st.title("InfiUse Chat App")

    # Add customization options to the sidebar
    st.sidebar.title('Select an LLM')
    model = st.sidebar.selectbox(
        'Choose a model',
        ['mixtral-8x7b-32768', 'llama3-8b-8192']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value=5)

    memory = ConversationBufferWindowMemory(k=conversational_memory_length)

    st.markdown("*Generally use Mistral model for code and Llama-3 for text related purposes*")

    # Initialize session state variables for chat history if not already initialized
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    current_chat_history = st.session_state.chat_history

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

    for message in current_chat_history:
        st.markdown(f"""
            <div style="float: right; width: 50%; border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 10px; background-color: #e0f2f1;">
                <h4 style="color: #2c3e50;">Human:</h4>
                <p>{message['human']}</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0; border-radius: 10px; background-color: #f0f8ff;">
                <h4 style="color: #2980b9;">AI:</h4>
                <p>{message['AI']}</p>
            </div>
        """, unsafe_allow_html=True)

    # Scroll to the bottom of the page after output is generated
    st.markdown("<script>window.scrollTo(0, document.body.scrollHeight);</script>", unsafe_allow_html=True)

    # User question text area covering full page width
    user_question = st.text_area("Ask a question:", key="user_question")

    if st.button("Submit"):
        user_question = st.session_state.user_question
        if user_question:
            # Use Groq AI to generate response
            response = conversation(user_question)
            message = {'human': user_question, 'AI': response['response']}
            current_chat_history.append(message)

            # Save current chat history back to session state
            st.session_state.chat_history = current_chat_history
            st.experimental_rerun()


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

    menu = ["Login", "Register", "Forgot Password"]
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

        if 'coins' not in st.session_state:
            st.session_state.coins = 0

        # Display coin meter at top-left corner of sidebar
        st.sidebar.markdown(f"💰 **Coins:** {st.session_state.coins}")



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


