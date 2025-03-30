import db

def add_thread(title, content, stock_market, sector, parent_or_origin, user_id):
    sql = """INSERT INTO threads (title, content, stock_market, sector, parent_or_origin, user_id)
            VALUES (?, ?, ?, ?, ?, ?)""" 
    
    db.execute(sql, [title, content, stock_market, sector, parent_or_origin, user_id])

def get_threads():
    sql = "SELECT id, title FROM threads ORDER BY id DESC"

    return db.query(sql)

def get_thread(thread_id):
    sql = """SELECT threads.id, 
                    threads.title, 
                    threads.content, 
                    threads.stock_market, 
                    threads.sector, 
                    threads.parent_or_origin, 
                    users.id user_id, 
                    users.username
        FROM threads, users
        WHERE threads.user_id = users.id AND 
            threads.id = ?"""
    
    return db.query(sql, [thread_id])[0]

def update_thread(thread_id, title, content, stock_market, sector, parent_or_origin):
    sql = """UPDATE threads SET title = ?,
                                content = ?,
                                stock_market = ?,
                                sector = ?,
                                parent_or_origin = ?
                            WHERE id= ?"""
    
    db.execute(sql, [title, content, stock_market, sector, parent_or_origin, thread_id])


def remove_thread(thread_id):
    sql = "DELETE FROM threads WHERE id = ?"
    
    db.execute(sql, [thread_id])

def find_thread(query):
    sql = """SELECT id, title
                FROM threads
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY id DESC"""
    return db.query(sql, ["%" + query + "%", "%" + query + "%"])
