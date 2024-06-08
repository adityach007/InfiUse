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
import json
import base64
import requests
from streamlit_ace import st_ace
import uuid
import time




load_dotenv()

groq_api_key = os.environ['GROQ_API_KEY']
API_KEY = os.environ["codestral_api"]

# The endpoint you want to hit
url = "https://codestral.mistral.ai/v1/chat/completions"

blog_posts_file = 'blog_posts.json'


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
