from flask import Flask, render_template, request, jsonify, url_for, redirect, session, flash
import os
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from pymongo import MongoClient
import google.generativeai as genai

load_dotenv()

# Set up the API key
genai.configure(api_key=os.getenv("AIzaSyDTRsHqUASYS5jbyZmzjb-5GcolDstVK4A"))

# Set up the model configuration and safety settings
generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Set up the model
model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Initialize a conversation
convo = model.start_chat(history=[
  {
    "role": "user",
    "parts": ["Create a concise AI chatbot for 12th-grade students, guiding them through career choices. The chatbot should ask strategic questions about course preferences, career goals, and interests, providing brief yet helpful advice. Ensure the conversation concludes with a tailored recommendation for a suitable career path. Prioritize a user-friendly interface for an efficient user experience"]
  },
  {
    "role": "model",
    "parts": ["**Chatbot:**\n\nHello, [User Name]! I'm here to help you explore your career options. Let's get started.\n\n1. What are your favorite subjects in school?\n\n\n2. What are your strengths and weaknesses?\n\n\n3. What are your hobbies and interests outside of school?\n\n\n4. What are your career goals and aspirations?\n\n\n5. What kind of work environment do you prefer?\n\n\n6. What kind of lifestyle do you want to have in the future?\n\n\n7. What are your salary expectations?"]
  },
  {
    "role": "user",
    "parts": ["hii"]
  },
  {
    "role": "model",
    "parts": ["Hello, hii! 👋\n\nI'm glad you're here. I'm here to help you with your career choices. 😊\n\nWhat's your name? I'd like to address you by name throughout our conversation."]
  },
  {
    "role": "user",
    "parts": ["i llike coding and photography"]
  },
  {
    "role": "model",
    "parts": ["Ah, coding and photography—two very different but fascinating fields! 📸💻\n\n1. Coding: opens up a world of possibilities in the tech industry. You could become a software engineer, web developer, data scientist, or even a cybersecurity expert. These roles are in high demand and offer great career prospects.\n\n2. Photography: allows you to capture and share your unique perspective with the world. You could pursue a career as a photojournalist, commercial photographer, portrait photographer, or even a wedding photographer. The creative and technical aspects of photography make it a rewarding field for many.\n\nNow, let's explore your options further. What are your strengths and weaknesses?\n\n(Your answer will help me identify areas where you excel and areas where you might need additional support.)"]
  },
  {
    "role": "user",
    "parts": ["hi"]
  },
  {
    "role": "model",
    "parts": ["Hi there! 😊\n\nI'm excited to help you explore your career options.\n\nWhat's your name? I'd like to address you by name throughout our conversation.\n\n(Please provide your name so I can personalize the conversation.)"]
  },
 
])

mode = 'cloud'

if mode == 'local':
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/chatbot'
    mongo = PyMongo(app)
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017") 
    db = client['chatbot']
else:
    app = Flask(__name__)
    app.secret_key = 'your_secret_key_here'
    app.config['MONGO_URI'] = 'mongodb://localhost:27017/chatbot'
    mongo = PyMongo(app)
    # Connect to MongoDB
    client = MongoClient("mongodb+srv://shiban:hqwaSJns8vkQVVtk@cluster0.6dhrc7h.mongodb.net/test") 
    db = client['chatbot']
    
app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loginregpage')
def loginregpage():
    return render_template('login.html')



@app.route("/register-success", methods=['POST'])
def homeregister():
    if request.method == 'POST':
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("new-password")
        confirmpwd = request.form.get("confirm-password")

        if not name or not email or not password or not confirmpwd:
            flash('All fields are required', 'error')
            return redirect(url_for('loginregpage'))

        if password != confirmpwd:
            flash('Passwords do not match', 'error')
            return redirect(url_for('loginregpage'))

        if db.chatbotuser.find_one({'email': email}):
            flash('Email already exists', 'error')
            return redirect(url_for('loginregpage'))

        db.chatbotuser.insert_one({'name': name, 'email': email, 'password': password})

        # Store user information in session after registration
        session['user'] = {'name': name, 'email': email}
        
        flash('Registration successful', 'success')
        return redirect(url_for('chatbotpage', username=name))

    return render_template('login.html')

@app.route("/login", methods=['POST'])
def logincred():
    if request.method == 'POST':
        email = request.form.get("email1")
        password = request.form.get("password")

        if not email or not password:
            flash('All fields are required', 'error')
            return redirect(url_for('loginregpage'))

        user = db.chatbotuser.find_one({'email': email, 'password': password})

        if user:
            # Extract the first name from the 'name' field
            full_name = user.get('name', '')
            if full_name and len(full_name.split()[0]) == 1:
                # If the first name is an initial, get the second name
                second_name = ' '.join(full_name.split()[1:])
                first_name = second_name if second_name else ''
            else:
                # If the first name is not an initial, get the first name
                first_name = full_name.split()[0] if full_name else ''

            # Store user ID and first name in session
            session['user'] = {'name': first_name, 'email': email}
            flash('Login successful', 'success')

            # Redirect to chatbotpage with the username in the URL
            return redirect(url_for('chatbotpage', username=first_name))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('loginregpage'))


@app.route('/chatbotpage')
def chatbotpage():
    # Retrieve user information from session
    user = session.get('user', None)

    # Check if user is logged in
    if user:
        # Pass the username to the template
        return render_template('chatbot.html', username=user['name'])
    else:
        # Redirect to login page if not logged in
        flash('Please log in first', 'error')
        return redirect(url_for('loginregpage'))

@app.route('/ask', methods=['POST'])
def ask():
    # Retrieve user input from the POST request
    user_input = request.form.get('user_message')

    # Send user input to the generative model
    convo.send_message(user_input)

    # Get the model's response
    bot_response = convo.last.text

    # Return the response in JSON format
    return jsonify({'bot_response': bot_response, 'user_input': user_input})


if __name__ == '__main__':
    app.run(debug=True)
