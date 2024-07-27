import sqlite3

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        user_id INTEGER,
        task TEXT,
        status TEXT
    )''')
    conn.commit()
    conn.close()

def add_task(user_id, task, status="pending"):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("INSERT INTO tasks (user_id, task, status) VALUES (?, ?, ?)", (user_id, task, status))
    conn.commit()
    conn.close()

def get_tasks(user_id, status=None):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    if status:
        c.execute("SELECT rowid, task FROM tasks WHERE user_id = ? AND status = ?", (user_id, status))
    else:
        c.execute("SELECT rowid, task, status FROM tasks WHERE user_id = ?", (user_id,))
    tasks = c.fetchall()
    conn.close()
    return tasks

def update_task_status(rowid, status):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("UPDATE tasks SET status = ? WHERE rowid = ?", (status, rowid))
    conn.commit()
    conn.close()

def delete_task(rowid):
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE rowid = ?", (rowid,))
    conn.commit()
    conn.close()
