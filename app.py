import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session, flash
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
        flash("VIRHE: Salasanat eivät täsmää", "error")
        return redirect("/register")
    
    if password1 == "" and password2 == "":
        flash("VIRHE: Syötä salasana")
        return redirect("/register")

    password_hash=generate_password_hash(password1)

    if username == "":
        flash("VIRHE: Syötä käyttäjätunnus")
        return redirect("/register")
    try:
        sql="INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        flash("VIRHE: Käyttäjätunnus on varattu", "error")
        return redirect("/register")
    
    flash("Käyttäjä tunnus luotu onnistuneesti", "success")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        sql_username="SELECT * FROM users WHERE username = ?"
        result_username=db.query(sql_username, [username])

        if result_username:

            if username == "":
                flash("VIRHE: Syötä käyttäjätunnus", "error")
                return redirect("/login")
            else:
                sql="SELECT id, password_hash FROM users WHERE username=?"
                result=db.query(sql, [username])[0]
                user_id=result["id"]
                password_hash=result["password_hash"]

            if check_password_hash(password_hash, password):
                session["user_id"]=user_id
                session["username"]=username
                flash("Kirjauduttu onnistuneesti", "success")
                return redirect("/")
            else:
                flash("VIRHE: väärä käyttäjätunnus tai salasana", "error")
                return redirect("/login")
        else:
            flash("VIRHE: Käyttäjätunnusta ei ole olemassa")
            return redirect("/login")
        

    
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

    if title == "" or content == "":
        flash("Lisää ensin otsikko sekä sisältö", "error")
        return redirect("/new_thread")

    threads.add_thread(title, content, stock_market, sector, parent_or_origin, user_id)

    return redirect("/")


@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    thread = threads.get_thread(thread_id)
    messages = threads.get_messages(thread_id)
    return render_template("show_thread.html", thread=thread, messages=messages)

@app.route("/edit_thread/<int:thread_id>")
def edit_thread(thread_id):
    thread = threads.get_thread(thread_id)
    if thread["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_thread.html", thread=thread)

@app.route("/update_thread", methods=["POST"])
def update_thread():
    thread_id = request.form["thread_id"]
    thread = threads.get_thread(thread_id)
    if thread["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    content = request.form["content"]
    stock_market = request.form["stock_market"]
    sector = request.form["sector"]
    parent_or_origin = request.form["parent_or_origin"]

    threads.update_thread(thread_id, title, content, stock_market, sector, parent_or_origin)

    return redirect("/thread/" + str(thread_id))

@app.route("/remove_thread/<int:thread_id>", methods=["GET", "POST"])
def remove_thread(thread_id):
    thread=threads.get_thread(thread_id)

    if thread["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_thread.html", thread=thread)
    
    if request.method == "POST":
        if "remove" in request.form:
            threads.remove_thread(thread_id)
            return redirect("/")
        else:
            return redirect("/thread/" + str(thread_id))



@app.route("/find_thread")
def find_thread():
    query = request.args.get("query")
    if query:
        results = threads.find_thread(query)
    else:
        query=""
        results=[]
    return render_template("find_thread.html",query=query, results=results)

@app.route("/thread/<int:thread_id>/add_message", methods=["POST"])
def add_message(thread_id):
    content = request.form["content"]
    user_id = session["user_id"]
    if "user_id" not in session:
        return redirect("/login")
    else:
        if content == "":
            flash("Kommentti ei voi olla tyhjä", "error")
            return redirect("/thread" + str(thread_id))
        else:
            threads.add_message(content, user_id, thread_id)
            return redirect("/thread/" + str(thread_id))
    
@app.route("/user/<int:user_id>")
def user_profile(user_id):
    sql="SELECT username FROM users WHERE id = ?"
    user=db.query(sql, [user_id])

    sql_threads = "SELECT id, title FROM threads WHERE user_id = ? ORDER BY id ASC"
    threads = db.query(sql_threads, [user_id])

    sql_messages = """SELECT messages.content, messages.sent_at, threads.id AS thread_id, threads.title AS thread_title
                    FROM messages JOIN threads ON messages.thread_id = threads.id
                    WHERE messages.user_id = ?
                    ORDER BY messages.sent_at"""
    messages = db.query(sql_messages, [user_id])

    sql_thread_count = "SELECT COUNT(threads.id) as count FROM threads WHERE user_id = ?"
    thread_count = db.query(sql_thread_count, [user_id])[0]["count"]
    sql_message_count = "SELECT COUNT(messages.id) as count FROM messages WHERE user_id = ?"
    message_count = db.query(sql_message_count, [user_id])[0]["count"]

    return render_template("user_profile.html", user = user[0], threads = threads, 
                           messages = messages, thread_count = thread_count, message_count = message_count)
