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

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")

# AWS credentials and region from environment variables
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
region_name = os.getenv("AWS_REGION", "ap-south-1")

# Connect to DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
)

# Tables
users_table = dynamodb.Table('travelgo_users')
trains_table = dynamodb.Table('trains')
bookings_table = dynamodb.Table('bookings')

# Example route: Home
@app.route('/')
def index():
    return render_template('index.html')

# Example: Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']

        users_table.put_item(Item={
            'username': username,
            'password': password,
            'email': email,
            'created_at': datetime.utcnow().isoformat()
        })

        flash("Registration successful!", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Example: Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        response = users_table.get_item(Key={'username': username})
        user = response.get('Item')

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# Dashboard page
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first', 'warning')
        return redirect(url_for('login'))

    return render_template('dashboard.html', username=session['username'])

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)