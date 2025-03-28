import db

def add_thread(title, content, stock_market, sector, parent_or_origin, user_id):
    sql = """INSERT INTO threads (title, content, stock_market, sector, parent_or_origin, user_id)
            VALUES (?, ?, ?, ?, ?, ?)""" 
    
    db.execute(sql, [title, content, stock_market, sector, parent_or_origin, user_id])
