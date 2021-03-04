from flask import Flask, render_template, request, url_for, redirect, session
import pymongo
import bcrypt

app = Flask(__name__)

app.secret_key = "testing"
client = pymongo.MongoClient("mongodb://localhost:27017/explog")
db = client.explog
records = db.users


@app.route('/')
def index():
    if "email" in session:
        email = session["email"]
        return render_template('index.html', email=email)
    else:
        return redirect(url_for("login"))


@app.route("/signup", methods=['post', 'get'])
def signup():
    message = ''
    if "email" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        
        #if found in database showcase that it's found 
        user_found = records.find_one({"username": username})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('signup.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('signup.html', message=message)
        else:
            #hash the password and encode it
            hashpass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            records.insert_one({'username': username, 'email': email, 'password': hashpass})
            
            session['email'] = email
   
            return redirect(url_for("index", email=email))
            # return render_template('index.html', email=new_email)

    return render_template('signup.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        #check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            #encode the password and check if it matches
            if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
                session["email"] = email_val
                return redirect(url_for('index'))
            else:
                if "email" in session:
                    return redirect(url_for("index"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)

    return render_template('login.html', message=message)


@app.route("/signout", methods=["POST", "GET"])
def signout():
    if "email" in session:
        session.pop("email", None)
        message = 'You are signed out!'
        return render_template('index.html', message=message)
    else:
        return redirect(url_for("index"))


#end of code to run it
if __name__ == "__main__":
  app.run(debug=True)