from flask import Flask, render_template, request, flash, session, redirect
import re
import md5,os, binascii
from mysqlconnection import MySQLConnector

app = Flask(__name__)
mysql = MySQLConnector(app,'registrationdb')
app.secret_key = 'This is not a secret key'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
# email compiler key is needed to check if the email is valid.

@app.route('/')
def index():                        
  return render_template('index.html') 

@app.route('/success')
def sucess():
  return render_template('success.html')
# @app.route('/login')
# def login():
#   form_valid = True
#   email = request.form['email']
#   password = request.form['password']
#   user_query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
#   query_data = {'email': email}
#   user = mysql.query_db(user_query, query_data)
#   if len(user) != 0:
#     encrypted_password = md5.new(password + user[0]['salt']).hexdigest()
#   if user[0]['password'] == encrypted_password:
#     flash('ok!')
#   elif len(request.form['password'])<8:
#     flash('password field requires at least 8 characters')
#     form_valid = False
#   elif request.form['password'] != request.form['cpassword']:
#     flash ('password do not match')
#     form_valid = False
#   if len(request.form['email']) <= 2:
#     flash('email needs to be filled out')
#     form_valid = False
#   elif not EMAIL_REGEX.match(request.form['email']):
#     flash("Invalid email")
#     form_valid = False
#   if form_valid == True:
#     return redirect('/hold')
#   elif form_valid == False:
#     return redirect('/')

@app.route('/register', methods=["POST"])

# check the database to make sure there is no duplicate emails inside
# the database

# connect to the database, insert records posted from a form, 
# retrieve records from a database and set a session/flash 
# for any error or success messages 

# 1. First Name - letters only, at least 2 characters and that it was submitted
# 2. Last Name \- letters only, at least 2 characters and that it was submitted
# 3. Email - Valid Email format, and that it was submitted
# 4. Password - at least 8 characters, and that it was submitted
# 5. Password Confirmation - matches password

def process_form():

  form_valid = True
  user = mysql.query_db('SELECT email from users WHERE email=:email ', {'email':request.form['email']})
  
  if user:
    flash('Duplicate email in database')
    form_valid = False
  # email address 
  if len(request.form['email']) <= 2:
    flash('email needs to be filled out')
    form_valid = False
  elif not EMAIL_REGEX.match(request.form['email']):
    flash("Invalid email")
    form_valid = False

  # first name validation
  if len(request.form['fname'])<2: 
    flash("first name needs at least two characters")
    form_valid = False
  elif not request.form["fname"].isalpha():
  # The method isalpha() checks whether the string consists of 
  # alphabetic characters only. In this case the numbers are not allowed
    flash("Invalid first name")
    form_valid = False

  # last name validation
  if len(request.form['lname'])<0:
    flash('last name field can not be empty')
    form_valid = False
  elif not request.form["lname"].isalpha():
    flash("Invalid last name")
    form_valid = False

  # password validation
  if len(request.form['password'])<8:
    flash('password field requires at least 8 characters')
    form_valid = False
  elif request.form['password'] != request.form['cpassword']:
    flash ('password do not match')
    form_valid = False

    # successful registration
  if form_valid:
    
    temp = request.form['password']
    salt =  binascii.b2a_hex(os.urandom(15))
    hash_pw = md5.new(temp + salt).hexdigest()

    query = "INSERT INTO users (fname, lname, email, password, pwsalt, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, :pwsalt, NOW(), NOW())"

    data = {
      'first_name': request.form['fname'],
      'last_name':  request.form['lname'],
      'email': request.form['email'],
      'password': hash_pw,
      'pwsalt': salt
    }
    myresult = mysql.query_db(query, data)
    return redirect('/success')
  return redirect('/')

app.run(debug=True)