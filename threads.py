import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)
    return classes

def add_thread(title, content, classes, parent_or_origin, user_id):
    all_classes = get_all_classes()

    sql = """INSERT INTO threads (title, content, parent_or_origin, user_id)
            VALUES (?, ?, ?, ?)""" 
    
    db.execute(sql, [title, content, parent_or_origin, user_id])

    thread_id=db.last_insert_id()

    sql = "INSERT INTO thread_classes (thread_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [thread_id, title, value])

def get_classes(thread_id):
    sql = "SELECT title, value FROM thread_classes WHERE thread_id = ?"
    return db.query(sql, [thread_id])

def get_threads():
    sql = "SELECT id, title FROM threads ORDER BY id DESC"

    return db.query(sql)

def get_thread(thread_id):
    sql = """SELECT threads.id, 
                    threads.title, 
                    threads.content,  
                    threads.parent_or_origin, 
                    users.id user_id, 
                    users.username
        FROM threads, users
        WHERE threads.user_id = users.id AND 
            threads.id = ?"""
    
    result = db.query(sql, [thread_id])
    if result:
        return result[0]
    else:
        None

def update_thread(thread_id, title, content, parent_or_origin, classes):
    sql = """UPDATE threads SET title = ?,
                                content = ?,
                                parent_or_origin = ?
                            WHERE id= ?"""
    
    db.execute(sql, [title, content, parent_or_origin, thread_id])

    sql = "DELETE FROM thread_classes WHERE thread_id = ?"
    db.execute(sql, [thread_id])

    sql = "INSERT INTO thread_classes (thread_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [thread_id, title, value])


def remove_thread(thread_id):
    sql_classes = "DELETE FROM thread_classes WHERE thread_id = ?"
    db.execute(sql_classes, [thread_id])
    sql_messages = "DELETE FROM messages WHERE thread_id =?"
    db.execute(sql_messages, [thread_id])
    sql_threads = "DELETE FROM threads WHERE id = ?"
    db.execute(sql_threads, [thread_id])

def find_thread(query):
    sql = """SELECT id, title
                FROM threads
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY id DESC"""
    return db.query(sql, ["%" + query + "%", "%" + query + "%"])


def add_message(content, user_id, thread_id):
    sql="""INSERT INTO messages (content, sent_at, user_id, thread_id)
            VALUES (?, datetime("now"), ?, ?)"""
    db.execute(sql, [content, user_id, thread_id])

def get_messages(thread_id):
    sql="""SELECT messages.id, messages.content, messages.sent_at, users.username
            FROM messages, users
            WHERE messages.user_id = users.id AND messages.thread_id = ? 
            ORDER BY messages.sent_at DESC"""
    return db.query(sql, [thread_id])

def get_images(thread_id):
    sql = "SELECT id FROM images WHERE thread_id = ?"
    return db.query(sql, [thread_id])

def add_image(thread_id, image):
    sql = "INSERT INTO images (thread_id, image) VALUES (?, ?)"
    db.execute(sql, [thread_id, image])

def get_image(image_id):
    sql = "SELECT image FROM images WHERE id = ?"
    result = db.query(sql, [image_id])
    return result[0][0] if result else None

def remove_image(thread_id, image_id):
    sql = "DELETE FROM images WHERE id = ? AND thread_id = ?"
    db.execute(sql, [image_id, thread_id])
    