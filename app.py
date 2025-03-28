import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import threads

app = Flask(__name__)
app.secret_key=config.secret_key

@app.route("/")
def index():
    all_threads = threads.get_threads()
    return render_template("index.html", threads=all_threads)

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username=request.form["username"]
    password1=request.form["password1"]
    password2=request.form["password2"]
    if password1!=password2:
        return "VIRHE: Salasanat eivät täsmää"
    password_hash=generate_password_hash(password1)

    try:
        sql="INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: Käyttäjätunnus on varattu"
    
    return "Käyttäjätunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        sql="SELECT id, password_hash FROM users WHERE username=?"
        result=db.query(sql, [username])[0]
        user_id=result["id"]
        password_hash=result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"]=user_id
            session["username"]=username
            return redirect("/")
        else:
            return "VIRHE: väärä käyttäjätunnus tai salasana"
    
@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")

@app.route("/new_post")
def new_post():
    return render_template("new_post.html")
    
@app.route("/new_thread", methods=["POST"])
def new_thread():
    title = request.form["title"]
    content = request.form["content"]
    stock_market = request.form["stock_market"]
    sector = request.form["sector"]
    parent_or_origin = request.form["parent_or_origin"]
    user_id = session["user_id"]

    threads.add_thread(title, content, stock_market, sector, parent_or_origin, user_id)

    return redirect("/")


@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    thread = threads.get_thread(thread_id)
    return render_template("show_thread.html", thread=thread)

@app.route("/edit_thread/<int:thread_id>")
def edit_thread(thread_id):
    thread=threads.get_thread(thread_id)
    return render_template("edit_thread.html", thread=thread)

@app.route("/update_thread", methods=["POST"])
def update_thread():
    thread_id=request.form["thread_id"]
    title = request.form["title"]
    content = request.form["content"]
    stock_market = request.form["stock_market"]
    sector = request.form["sector"]
    parent_or_origin = request.form["parent_or_origin"]

    threads.update_thread(thread_id, title, content, stock_market, sector, parent_or_origin)

    return redirect("/thread/" + str(thread_id))

@app.route("/remove_thread/<int:thread_id>", methods=["GET", "POST"])
def remove_thread(thread_id):
    if request.method == "GET":
        thread=threads.get_thread(thread_id)
        return render_template("remove_thread.html", thread=thread)
    
    if request.method == "POST":
        if "remove" in request.form:
            threads.remove_thread(thread_id)
            return redirect("/")
        else:
            return redirect("/thread/" + str(thread_id))


