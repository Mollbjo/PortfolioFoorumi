import db
from werkzeug.security import generate_password_hash, check_password_hash

def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def user_threads(user_id):
    sql_threads = "SELECT id, title FROM threads WHERE user_id = ? ORDER BY id ASC"
    return db.query(sql_threads, [user_id])

def user_messages(user_id):
    sql_messages = """SELECT messages.content, messages.sent_at, threads.id AS thread_id, threads.title AS thread_title
                    FROM messages JOIN threads ON messages.thread_id = threads.id
                    WHERE messages.user_id = ?
                    ORDER BY messages.sent_at"""
    return db.query(sql_messages, [user_id])

def user_thread_count(user_id):
    sql_thread_count = "SELECT COUNT(threads.id) as count FROM threads WHERE user_id = ?"
    return db.query(sql_thread_count, [user_id])[0]["count"]

def user_message_count(user_id):
    sql_message_count = "SELECT COUNT(messages.id) as count FROM messages WHERE user_id = ?"
    return db.query(sql_message_count, [user_id])[0]["count"]

def create_user(username, password):
    password_hash=generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def user_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id=result[0]["id"]
    password_hash = result[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    else:
        return None





