from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from bson.objectid import ObjectId
from bson.errors import InvalidId
import os
from dotenv import load_dotenv
import boto3

# Load environment variables from .env file
load_dotenv()

app = Flask(___name__)  # ✅ Corrected __name_
app.secret_key = os.getenv('43be6c76e9b767a5d2b8684106fcaf1f2169a56b190a3135feaab49110b8e767', 'default_secret_key')

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client['travelgo']
users_collection = db['users']

# Home page
@app.route('/')
def home():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        users_collection.insert_one({
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.now()
        })
        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({'email': email})
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))
    return render_template('dashboard.html', name=session['user_name'])

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# Error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
