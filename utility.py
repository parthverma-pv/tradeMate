import sqlite3

def get_user_id(username):
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user_id = c.fetchone()[0]
    conn.close()
    return user_id