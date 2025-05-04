import sqlite3
from flask import Flask
from flask import abort, redirect, render_template, request, session, flash
import config
import db
import threads
import users

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

    if len(password1) < 8 or len(password2) < 8:
        abort(403)
    
    if password1 == "" and password2 == "":
        flash("VIRHE: Syötä salasana", "error")
        return redirect("/register")

    if username == "":
        flash("VIRHE: Syötä käyttäjätunnus", "error")
        return redirect("/register")
    if len(username) > 25:
        abort(403)

    try: 
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("VIRHE: Käyttäjätunnus on varattu", "error")
        return redirect("/register")
    
    flash("Käyttäjä luoto onnistuneesti", "success")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")

    if request.method=="POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "":
            flash ("VIRHE: Syötä käyttäjätunnus", "error")
            return redirect("/login")

        user_id = users.user_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            flash ("VIRHE: Väärä käyttäjätunnus tai salasana", "error")
            return redirect("/login")
        
def check_login():
    if "user_id" not in session:
        abort(403)
    
@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")

@app.route("/new_post")
def new_post():
    check_login()

    return render_template("new_post.html")
    
@app.route("/new_thread", methods=["POST"])
def new_thread():
    check_login()

    title = request.form["title"]
    content = request.form["content"]
    stock_market = request.form["stock_market"]
    sector = request.form["sector"]
    parent_or_origin = request.form["parent_or_origin"]
    user_id = session["user_id"]

    if len(title) > 50 or len(content) > 1000 or len(stock_market) > 10 or len(sector) > 20 or len(parent_or_origin) > 20:
        abort(403)

    if title == "" or content == "":
        flash("Lisää ensin otsikko sekä sisältö", "error")
        return redirect("/new_thread")

    threads.add_thread(title, content, stock_market, sector, parent_or_origin, user_id)

    return redirect("/")


@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    thread = threads.get_thread(thread_id)
    messages = threads.get_messages(thread_id)
    if not thread:
        abort(404)
    return render_template("show_thread.html", thread=thread, messages=messages)

@app.route("/edit_thread/<int:thread_id>")
def edit_thread(thread_id):
    check_login()

    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_thread.html", thread=thread)

@app.route("/update_thread", methods=["POST"])
def update_thread():
    check_login()

    thread_id = request.form["thread_id"]
    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    content = request.form["content"]
    stock_market = request.form["stock_market"]
    sector = request.form["sector"]
    parent_or_origin = request.form["parent_or_origin"]

    if title == "" or content == "":
        flash("Lisää ensin otsikko sekä sisältö", "error")
        return redirect("/edit_thread/" + str(thread_id))

    if len(title) > 50 or len(content) > 1000 or len(stock_market) > 10 or len(sector) > 20 or len(parent_or_origin) > 20:
        abort(403)

    threads.update_thread(thread_id, title, content, stock_market, sector, parent_or_origin)

    return redirect("/thread/" + str(thread_id))

@app.route("/remove_thread/<int:thread_id>", methods=["GET", "POST"])
def remove_thread(thread_id):
    thread=threads.get_thread(thread_id)

    check_login()

    if not thread:
        abort(404)

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
    user = users.get_user(user_id)
    threads = users.user_threads(user_id)
    messages = users.user_messages(user_id)
    thread_count = users.user_thread_count(user_id)
    message_count = users.user_message_count(user_id)
    if not user:
        abort(404)
    return render_template("user_profile.html", user=user, threads=threads, messages=messages, thread_count=thread_count, message_count=message_count)
