from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import random
import string
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask import session
from werkzeug.utils import secure_filename
import os
import smtplib
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

users = {}



# MongoDB setup
uri = "mongodb+srv://webAi:1234@cluster0.l8xvws7.mongodb.net/web-Ai?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# Get the database
db = client.your_database_name

# Get the collection
users_collection = db.users
blog_collection = db.blogs 

# Fetch all documents in the collection
all_users = users_collection.find()
blog_users = blog_collection.find()

# Iterate over the documents and print them

# Fetch only the 'username' and 'email' fields for each user
all_users = users_collection.find({}, {'username': 1, 'email': 1})

# Iterate over the documents and print the 'username' and 'email'


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = client.your_database_name.users.find_one({'username': username})
        
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('profile', username=username))
        else:
            return "Invalid username or password", 401
    
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the home page
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email= request.form['email']
        password = request.form['password']

        if username not in users:
            client.your_database_name.users.insert_one({'username': username, 'name': name, 'email': email, 'password': password, 'chathistory': []})
            return redirect(url_for('login'))
            
    return render_template('register.html')


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        
        email = request.form.get('email')
        user = client.your_database_name.users.find_one({'email': email})
        


        if email in user:
            
            code = ''.join(random.choices(string.digits, k=6))
            print(code)

            msg = EmailMessage()
            msg.set_content(f'Your verification code is: {code}')

            msg['Subject'] = 'Password Reset Verification Code'
            msg['From'] = 'admin@gmail.com'
            msg['To'] = email

            try:
                server = smtplib.SMTP('smtp.example.com', 587)
                server.starttls()
                server.login('admin@example.com', 'password')
                server.send_message(msg)
                server.quit()
                print(f'Code sent to {email}')
            except Exception as e:
                print(f'Error sending code to {email}: {e}')

            # Redirect to the change password page with the email and code
            return redirect(url_for('change_password', email=email, code=code))

        else:
            return jsonify({"success": False, "message": "Email not found."}), 404

    return render_template('forget_password.html')

@app.route('/change_password',methods=['GET', 'POST'])
def change_password():

    if request.method == 'POST':
        new_password = request.json.get('password')




@app.route('/profile/<username>')
def profile(username):
    # Check if the username in the session matches the requested username
    if 'username' in session and session['username'] == username:
        # Fetch the user's data from the MongoDB database
        user_data = client.your_database_name.users.find_one({'username': username})
        
        # Pass the user's data to the template
        return render_template('profile.html', user=user_data)
    else:
        return "User not found", 404

# New route for AI chat
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    username = session.get('username', 'default_user')
    messages = []
    if request.method == 'POST':
        message = request.form['message']
        # Process the message using the Hugging Face API
        output = query({"inputs": message})
        # Adjust this line based on the actual structure of the API response
        # For example, if the response is a list and the AI's response is the first element:
        ai_response = output[0] if output else 'AI response not available'

        # Assuming each user has a chat history
        # Use the username from the session
        user_data = client.your_database_name.users.find_one({'username': username})
        if username not in user_data:
            user_data = client.your_database_name.users.find_one({'username': username})
            users[username] = {'chathistory': []}
        users[username]['chathistory'].append({'type': 'user', 'text': message})
        users[username]['chathistory'].append({'type': 'ai', 'text': ai_response})
        with open('users.json', 'w') as f:
            json.dump(users, f)
        return redirect(url_for('chat'))
    if username in users:
        messages = users[username]['chathistory']
    return render_template('chat.html', messages=messages)

@app.route('/admin', methods=['GET', 'POST'])
def print_json_db():
    if request.method == 'POST':
        # Define the expected admin ID and password
        admin_id = 'admin'
        admin_email = 'tawkirarifin200@gmail.com' 
        admin_password = 'password'

        # Get the ID and password from the form data
        provided_id = request.form.get('id')
        provided_password = request.form.get('password')

        # Check if the provided ID and password match the expected values
        if provided_id == admin_id and provided_password == admin_password:
            return redirect(url_for('table'))
            # try:
            #     with open('users.json', 'r') as f:
            #         users = json.load(f)
            #     return jsonify(users)
            # except FileNotFoundError:
            #     return "JSON database file not found", 404
        else:
            return "Invalid ID or password", 401
    return render_template('admin.html')

@app.route('/upload_blog', methods=['GET', 'POST'])
def upload_blog():
    
    username = session.get('username', 'default_user')
    user_data = client.your_database_name.users.find_one({'username': username})

    if request.method == 'POST':
        text = request.form['text']
        image = request.files['image']
        comment = request.form['comment']
        rating = request.form.get('rating')  # Assuming rating is optional

        if image and image.filename!= '':
            image_filename = secure_filename(image.filename)
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
            image_path = os.path.join('uploads', image_filename)
            image.save(image_path)

        # Check if the 'blogs' field exists in the user's document
        user_blogs = client.your_database_name.blog.find_one({'username': username})
        if user_blogs==None or 'blogs' not in user_blogs:
            # Initialize the 'blogs' field as an empty array
            client.your_database_name.blog.update_one(
                {'username': username},
                {'$set': {'blogs': []}},
                upsert=True)

        
        client.your_database_name.blog.update_one(
            {'username': username},
            {'$push': {
                'blogs': {
                    'text': text,
                    'image': image_path,
                    'comment': [comment],  # Wrap the comment in an array
                    'rating': rating
                }
            }},
            upsert=True)

        return redirect(url_for('blogpost'))  
            

        # Process the comment and rating as needed
        # For example, save them to a database

        # Redirect to a success page or back to the form
            
        # if username not in blog:
        #         blog[username] = {'text': text, 'image':image_path ,'comment':comment,'rating':rating}
        #         with open('blog.json', 'w') as f:
        #            json.dump(blog, f)

    return render_template('upload_blog.html', user=user_data)

@app.route('/blogpost')
def blogpost():
    blog = list(blog_collection.find())

    return render_template('blogpost.html', blog=blog)

@app.route('/add_comment_reaction', methods=['POST'])
def add_comment_reaction():
    # Retrieve the blog ID, comment, and reaction from the form data
    blog_id = request.form['blog_id']
    comment = request.form['comment']
    reaction = request.form['reaction']

    # Update the blog document in the MongoDB database with the new comment and reaction
    # blog_collection.update_one({'_id': ObjectId(blog_id)}, {'$set': {'comments': comment, 'reactions': reaction}})

    # Redirect back to the blog post page
    return redirect(url_for('blogpost', blog_id=blog_id))

@app.route('/table', methods=['GET', 'POST'])
def table():
    return render_template('table.html')


if __name__ == '__main__':
    app.run(debug=True)
