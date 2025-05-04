import sqlite3
from flask import Flask
from flask import abort, make_response, redirect, render_template, request, session, flash
import config
import db
import threads
import users
import secrets
import markupsafe

app = Flask(__name__)
app.secret_key=config.secret_key

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    all_threads = threads.get_threads()
    if "user_id" in session:
        user_id = session["user_id"]
        user = session["username"]
        return render_template("index.html", threads=all_threads, user_id=user_id, user=user)
    
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
            session["csrf_token"] = secrets.token_hex(16)
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

    classes = threads.get_all_classes()

    return render_template("new_post.html", classes=classes)
    
@app.route("/new_thread", methods=["POST"])
def new_thread():
    check_login()
    check_csrf()

    title = request.form["title"]
    content = request.form["content"]
    parent_or_origin = request.form["parent_or_origin"]
    user_id = session["user_id"]

    all_classes = threads.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            parts = entry.split(":")
            if parts[0] not in all_classes:
                abort(403)
            if parts[1] not in all_classes[parts[0]]:
                abort(403)
            classes.append((parts[0], parts[1]))



    if len(title) > 50 or len(content) > 1000 or len(parent_or_origin) > 20:
        abort(403)

    if title == "" or content == "":
        flash("Lisää ensin otsikko sekä sisältö", "error")
        return redirect("/new_thread")

    threads.add_thread(title, content, classes, parent_or_origin, user_id)

    thread_id = db.last_insert_id()
    return redirect("/thread/" + str(thread_id))

@app.route("/thread/<int:thread_id>")
def show_thread(thread_id):
    thread = threads.get_thread(thread_id)
    messages = threads.get_messages(thread_id)
    if not thread:
        abort(404)
    classes = threads.get_classes(thread_id)
    images = threads.get_images(thread_id)
    return render_template("show_thread.html", thread=thread, messages=messages, classes=classes, images=images)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = threads.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.route("/images/<int:thread_id>")
def edit_images(thread_id):
    check_login()

    thread=threads.get_thread(thread_id)
    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)

    images = threads.get_images(thread_id)

    return render_template("images.html", thread=thread, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    check_login()
    check_csrf()

    thread_id=request.form["thread_id"]

    thread=threads.get_thread(thread_id)

    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if not file.filename.endswith(".jpg"):
        return "VIRHE: väärä tiedostomuoto"

    image = file.read()
    if len(image) > 100 * 1024:
        return "VIRHE: liian suuri kuva"

    
    threads.add_image(thread_id, image)
    return redirect("/images/" + str(thread_id))


@app.route("/edit_thread/<int:thread_id>")
def edit_thread(thread_id):
    check_login()

    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)


    all_classes = threads.get_all_classes()
    classes={}
    for thread_class in all_classes:
        classes[thread_class] = ""
    for entry in threads.get_classes(thread_id):
        classes[entry["title"]] = entry["value"] 

    return render_template("edit_thread.html", thread=thread, classes=classes, all_classes=all_classes)

@app.route("/update_thread", methods=["POST"])
def update_thread():
    check_login()
    check_csrf()

    thread_id = request.form["thread_id"]
    thread = threads.get_thread(thread_id)
    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    content = request.form["content"]
    parent_or_origin = request.form["parent_or_origin"]

    if title == "" or content == "":
        flash("Lisää ensin otsikko sekä sisältö", "error")
        return redirect("/edit_thread/" + str(thread_id))

    if len(title) > 50 or len(content) > 1000 or len(parent_or_origin) > 20:
        abort(403)

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            parts = entry.split(":")
            if parts[0] not in all_classes:
                abort(403)
            if parts[1] not in all_classes[parts[0]]:
                abort(403)
            classes.append(parts[0], parts[1])

    threads.update_thread(thread_id, title, content, parent_or_origin, classes)

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
        check_csrf()
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
    check_login()
    check_csrf()
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

@app.route("/remove_images", methods=["POST"])
def remove_images():
    check_login()
    check_csrf()

    thread_id=request.form["thread_id"]

    thread=threads.get_thread(thread_id)

    if not thread:
        abort(404)
    if thread["user_id"] != session["user_id"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        threads.remove_image(thread_id, image_id)
    return redirect("/images/" + str(thread_id))
