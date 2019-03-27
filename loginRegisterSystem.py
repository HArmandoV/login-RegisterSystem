import hashlib, os, base64
from flask import Flask, request, render_template
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['accounts_database']
collection = db['accounts']
app = Flask(__name__)

@app.route('/', methods=["GET"])
def principalPage():
    return render_template('welcome.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":
        # Do signup stuff
        if request.form['password'] != request.form['confirm-password']:
            return "Passwords don't match!"
        elif bool(collection.find_one({'Username': request.form['username']})):
            return "Account already exists!"
        else:
            username = request.form['username']
            password = request.form['password']
            salt = str(base64.b64encode(os.urandom(16)))
            password_hash = hashlib.sha3_224(
                str(password + salt).encode('utf-8')
            ).hexdigest()
            to_db = {
                'Username': username,
                'Password': password_hash,
                'Salt'    : salt
            }
            collection.insert_one(to_db)
            return str("Created account " + username + ", congratulation!")

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if bool(collection.find_one({"Username": username})):
            # Username exists, do login
            salt = collection.find_one({"Username": username})['Salt']
            password_hash = hashlib.sha3_224(str(password + salt).encode('utf-8')).hexdigest()
            if password_hash == collection.find_one({"Username": username})['Password']:
                #Password hash matches
                return str("Successfully logged in as " + username + ", welcome!")
            else:
                return str("Incorrect password for " + username + ", sorry!")
        else:
            #Username doesn't exist
            return str("Can't find account " + username + ". Please, create an account!")

if __name__ == '__main__':
    app.run()
