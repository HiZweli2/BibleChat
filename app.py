from flask import Flask, redirect,url_for, render_template, request,session,jsonify
from flask_cors import CORS
from functools import wraps
import secrets
import boto3
import pymysql
import os


# Configure application
app = Flask(__name__)
CORS(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Initialize AWS SDK and configure Cognito settings
app.secret_key = secrets.token_hex()
serverSession = boto3.Session(profile_name = "your_aws_profile")
cognito_client = serverSession.client('cognito-idp', region_name='us-east-1')
user_pool_id = 'cognito_user_pool_id'
client_id = 'cognito_app_client_id'

# configure mysql settings
# Note these settings are specifically set in a way that your api will connect to aws rds through an EC2 jump server
# https://repost.aws/knowledge-center/rds-connect-ec2-bastion-host
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.Python.html
ENDPOINT="jumpserver_endpoint"
TokenENDPOINT = "rds_endpoint"
TokenPort = "rds_port_(this must be an int)"
PORT="jumpserver_local_port(this must be an int)"
USER="your_database_username"
REGION="us-east-1"
DBNAME="name_of_your_database"
os.environ['LIBMYSQL_ENABLE_CLEARTEXT_PLUGIN'] = '1'

#gets the credentials from .aws/credentials
mysql_client = serverSession.client('rds')
mysql_token = mysql_client.generate_db_auth_token(DBHostname=TokenENDPOINT, Port=TokenPort, DBUsername=USER, Region=REGION)

try:
    print("Trying to connect to mysqldb")
    conn = pymysql.connect(host=ENDPOINT,user=USER,passwd=mysql_token,port=PORT,database=DBNAME,ssl_ca='static/rds-ca-2019-root.pem')
    cur = conn.cursor()
    print("connected to Database")
    cur.execute("""SELECT now()""")
    query_results = cur.fetchall()
    print(query_results)
except Exception as e:
    print("Database connection failed due to {}".format(e)) 

# custom decorator that checks if user is logged in before processing api request  
def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET','POST'])
def register_user():
    if request.method == "POST":
        loginIssue = ''
        try:
            # Get user data from the request form
            username = request.form['username']
            password = request.form['password']
            isPastor = request.form['isPastor']
            email = request.form['email']

            # Call Cognito API to create the user
            response = cognito_client.sign_up(
                ClientId=client_id,
                Username=username,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                ],
            )
            # If successful, Cognito will send a confirmation code to the user's email
            print("message User registered successfully. Please check email for a confirmation code.", 200)
            print("searching database for pastors")
            cur.execute("SELECT * FROM users WHERE groupID = %s",0)
            result = cur.fetchall()
            # Get list of pastors in the database
            pastors = []
            for pastorInfo in result:
                pastorIdName = ""
                for i in range(len(pastorInfo)):
                    pastorIdName += str(pastorInfo[i])
                    pastorIdName += " " if i < 1 else ""
                    if i == 1:
                        pastors.append(pastorIdName)
                        break
            return render_template("emailVerification.html", username=username , password=password , isPastor=isPastor, pastors=pastors, email=email)
        except Exception as e:
            loginIssue = str(e)
        finally:
            return render_template("invalidLogin.html",loginIssue=loginIssue)
    else:
        return render_template("register.html")

# This function initates authentication and returns an user access token
def get_access_token(username, password, client_id):
    try:
        response = cognito_client.initiate_auth(
            ClientId=client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            },
        )
        return response['AuthenticationResult']['AccessToken']
    except Exception as e:
        print("Error during authentication:", e)
        return None

@app.route('/emailVerification', methods=['GET','POST'])
def emailVerification():
    if request.method == "POST":
        confirmationCode = request.form.get("confirmationCode")
        username = request.form.get("username")
        print(username)
        password = request.form.get("password")
        print(password)
        email = request.form.get("email")
        #Check if user registered as a pastor
        isPastor = request.form.get("isPastor")
        if isPastor == "pastor":
            pastorId = 0
        else:
            pastor = request.form.get("pastors")
            # Get Pastor id from pastor string
            pastorId = int(pastor.split()[0])
        loginIssue = ''
        try:
            print("message: Now sending ConfirmationCode " + confirmationCode  + " to cognito")
            response = cognito_client.confirm_sign_up(
            ClientId=client_id,
            Username=username,
            ConfirmationCode=confirmationCode
        )
            print("message: User email verified successfully. Now logging user in.", 200)
            print("message: getting access token from cognito")
            accessToken = get_access_token(username, password, client_id)
            print("message: Sending user information to mysqldb")
            #Now create user on mysqlDB
            try:
                query_results = cur.callproc('create_user',(username,email,accessToken,pastorId))
                conn.commit()
                print(query_results)
                print("message: New user created on mysqldb :)")
                return redirect("/login")
            except  conn.Error as e:
                print(f"Error: {e}")
                loginIssue = str(e)
            finally:
                return render_template("invalidLogin.html",loginIssue=loginIssue)
                # Handle the error, query was not executed successfully
        except Exception as exception:
            loginIssue = str(exception)
        finally:
            return render_template("invalidLogin.html",loginIssue=loginIssue)
    else:
       return render_template("emailVerification.html" , isPastor= request.args.get("isPastor"))
    
# Save current user information Globally for later use
updatedUserToken = []

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        print("Getting user name and password from form")
        username = request.form.get("username")
        password = request.form.get("password")
        loginIssue = ''
        # Ensure username was submitted
        print("Checking if username and password were provided by user")
        if not request.form.get("username"):
            loginIssue = "Error: must provide username"
            print("Error: must provide username")
            return render_template("invalidLogin.html", loginIssue=loginIssue)

        # Ensure password was submitted
        elif not request.form.get("password"):
            loginIssue = "must provide password"
            print("Error: must provide password")
            return render_template("invalidLogin.html", loginIssue=loginIssue)

        # sigin/authenticate the user with cognito
        print("authenticating/siging in user through cognito")
        accessToken = get_access_token(username, password, client_id)
        print("User authenticated :)")

        # Query database for username
        print("Now checking if user exists in mysqldb")
        cur.execute("SELECT * FROM users WHERE username = %s", username)
        user = cur.fetchall()

        # Ensure username exists in mysqldb
        if len(user) != 1 :
            loginIssue = "User not in mysqldb"
            print("Error: User not in mysqldb", 403)
            return render_template("invalidLogin.html", loginIssue=loginIssue)

        elif user[0][6] == 1:
            loginIssue = "User is marked as deleted in mysqldb"
            print("Error: User is marked as deleted in mysqldb", 403)
            return render_template("invalidLogin.html", loginIssue=loginIssue)
        
        #insert current user accessToken into users table in mysqldb
        print("Inserting current user access token in mysqldb")
        cur.execute("UPDATE users SET access_token = %s WHERE username = %s", (accessToken,username))
        conn.commit()
        
        # Get updated user token from mysqldb
        print("Gettting updated user token from  mysqldb")
        cur.execute("SELECT * FROM users WHERE username = %s", username)
        userData = cur.fetchall()
        updatedUserToken.append(userData[0])
        session['user_id'] = userData[0][0]
        session['user_token'] = userData[0][3]
        session['user_pastor'] = userData[0][4]
        # Redirect user to home page
        print("signin process complete now redirecting user to home page")
        # Get the available bible books, chapters , and verses
        print("get available books in the database")
        cur.execute("SELECT book FROM niv GROUP BY book")
        availableBooks = cur.fetchall()
        # Get user chats
        user_id = session['user_id']
        cur.callproc("get_chats",[user_id])
        chats = cur.fetchall()
        #Get list of all users
        cur.execute("SELECT id,username FROM users")
        users = cur.fetchall()
        return render_template("index.html", username=username, books=availableBooks, chats=chats, user_id=user_id,users=users)
    else:
        return render_template("login.html")

@app.route("/currentUserInfor")
def currentUserInfor():
    return jsonify(updatedUserToken[0])

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/getChapterAndVerse", methods=['POST'])
@login_required
def getChapterAndVerse():
    data = request.get_json()
    book = data.get("book")
    chapter = data.get("chapter")
    verse = data.get("verse")
    if book != "book" and verse == None and chapter == "chapter":
        cur.callproc('get_availableChapters',[book])
        chapters = cur.fetchall()
        return jsonify(chapters)
    elif book != "book" and chapter != "chapter":
        cur.callproc('get_availableVerses',[book,int(chapter)])
        verses = cur.fetchall()
        return jsonify(verses)
    return jsonify("Error quering verse or chapter :(")

@app.route("/getScripture", methods=['POST'])
@login_required
def getScripture():
    data = request.get_json()
    book = data.get("book")
    chapter = data.get("chapter")
    verse = data.get("verse")
    print("Book: " + book)
    print("Chapter: "+ chapter)
    print("verse: "+ verse)
    cur.execute("SELECT word FROM niv WHERE book = %s AND chapter = %s AND verse = %s",(book,int(chapter),int(verse)))
    scripture = cur.fetchall()[0][0]
    return jsonify(scripture)

@app.route("/", methods=["GET","POST"])
@login_required
def index():
    if request.method == "POST":
        data = request.get_json()
        cur.execute("SELECT book FROM niv GROUP BY book")
        availableBooks = cur.fetchall()
        sender = session['user_id'] 
        receiver = session['user_pastor'] 
        scripture = data.get("scripture")
        message = data.get("message")
        recipient = data.get("recipient")
        print(scripture)
        if sender != None and receiver != None and message != None and recipient != None and recipient != "users":
            if scripture != None:
                cur.callproc("send_message", (sender,recipient,scripture.rstrip('\n'),message))
                conn.commit()
                return jsonify("Message sent")
            else:
                cur.callproc("send_messageWithNoScripture", (sender,recipient,message))
                conn.commit()
                return jsonify("Message sent")
        return jsonify("Not sent")
    else:
        # Get the available bible books, chapters , and verses
        print("get available books in the database")
        cur.execute("SELECT book FROM niv GROUP BY book")
        availableBooks = cur.fetchall()
        # Get user chats
        user_id = session['user_id']
        cur.callproc("get_chats",[user_id])
        chats = cur.fetchall()
        # Get list of all users
        cur.execute("SELECT id,username FROM users")
        users = cur.fetchall()
        return render_template("index.html",books=availableBooks, chats=chats, user_id=user_id,users=users)

