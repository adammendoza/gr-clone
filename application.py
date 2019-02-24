import os
import json
from gr_request import get_gr_info
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def set_session(username):
    users = db.execute("SELECT id FROM users WHERE username = :username",{"username": username}).fetchall()
    for user in users:
        session["user_id"] = user.id
    

#registration landing page
@app.route("/")
@app.route("/register")
def register():
    if session.get("user_id") is None:
        return render_template("signup.html")
    else:
        return render_template("search.html")

    
@app.route("/check_signup", methods=["POST"])
def check_signup():
    username = request.form.get("username")
    p1 = request.form.get("password1")
    p2 = request.form.get("password2")
    
    if p1 != p2:
        return render_template("signup_failed_pw.html")

    #calls exception when username is not unique
    try:
        db.execute("INSERT INTO users (username, password) VALUES(:username, :password)",
        {"username": username, "password": p1})
        db.commit()
            
    except:
        return render_template("signup_failed_un.html")
    
    set_session(username)
    return render_template("search.html")


@app.route("/login")
def login():

    session["user_id"] = None
    return render_template("login.html")


@app.route("/check_login", methods=["POST"])
def check_login():
    username = request.form.get("username")
    password = request.form.get("password")

    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}) == None:
        return render_template("login_failed.html")

    else:
        
        set_session(username)
        return render_template("search.html", id=session["user_id"])


@app.route("/search", methods=["POST"])
def search():
    searched = request.form.get("search_request")
    searched = f"%%{searched}%%"

    items = db.execute("""SELECT * FROM books WHERE isbn LIKE :string
                        OR author LIKE :string 
                        OR title LIKE :string;""",
                        {"string": searched}).fetchall()

    
    if not items:
        return render_template("no_results.html") 
        
    return render_template("search_results.html", items=items)


@app.route("/bk_pg/<int:id>", methods=["POST", "GET"])
def book_page(id):

    book = db.execute("SELECT * FROM books WHERE id=:id",{"id": id}).fetchone()
    gr_data = get_gr_info(book.isbn)

    if request.method == "POST":
        if db.execute("SELECT * FROM reviews WHERE user_id=:user_id and isbn=:isbn",{"user_id": session["user_id"], "isbn": book.isbn}).fetchone() is None:

            review = request.form.get("review")
            star = request.form['options']
            db.execute("INSERT INTO reviews (isbn, review, user_id, rating) VALUES (:isbn, :review, :user_id, :rating)",
            {"isbn": book.isbn, "review": review, "user_id": session["user_id"], "rating": star})

            db.commit()

        else:
            reviews = db.execute("SELECT * FROM reviews WHERE isbn=:isbn ORDER BY posted_date DESC", {"isbn": book.isbn}).fetchall()
            return render_template("bk_pg_postfailed.html", book=book, reviews=reviews, gr_data=gr_data)

    reviews = db.execute("SELECT * FROM reviews WHERE isbn=:isbn ORDER BY posted_date DESC", {"isbn": book.isbn}).fetchall()
    return render_template("bk_pg.html", book=book, reviews=reviews, gr_data=gr_data)

    
#api routes /api/isbn 
@app.route("/api/<string:isbn>")
def getinfo(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
            {"isbn": isbn}).fetchone()

    if book == None:
        return "Error, Book not found."

    if book[5] != None:
        data = {
                "title": book[2],
                "author": book[3],
                "year": book[4],
                "isbn": book[1],
                "review_count": book[5],
                "average_score": book[6]
            }
    else:   
        data = {
                "title": book[2],
                "author": book[3],
                "year": book[4],
                "isbn": book[1],
                "review_count": 0,
                "average_score": 0.0
            }  
    return json.dumps(data)
