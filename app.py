from flask import Flask, request, jsonify, render_template, session
import sqlite3

app = Flask(__name__)
app.secret_key = "student-task-manager-secret-key"

def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            due_date TEXT
        )
    """)

    columns = conn.execute("PRAGMA table_info(tasks)").fetchall()

    column_names = [column["name"] for column in columns]

    if "due_date" not in column_names:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN due_date TEXT"
        )

    if "user_id" not in column_names:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN user_id INTEGER"
        )

    conn.commit()
    conn.close()


create_table()

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({
            "error": "All fields are required"
        }), 400

    conn = get_db_connection()

    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()

        return jsonify({
            "error": "Email already registered"
        }), 400

    conn.close()

    return jsonify({
        "message": "Registration successful"
    }), 200
    
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    conn = get_db_connection()

    user = conn.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, password)
    ).fetchone()

    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]

        return jsonify({
            "message": "Login successful"
        }), 200

    return jsonify({
        "error": "Invalid email or password"
    }), 401
    
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add_task", methods=["POST"])
def add_task():

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401

    data = request.get_json()

    task = data.get("task")
    due_date = data.get("due_date")

    if not task or not due_date:
        return jsonify({
            "error": "Task and due date are required"
        }), 400

    conn = get_db_connection()

    conn.execute(
        """
        INSERT INTO tasks
        (task, due_date, completed, user_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            task,
            due_date,
            0,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task added successfully"
    }), 200
    data = request.get_json()

    task = data.get("task")
    due_date = data.get("due_date")

    if not task or not due_date:
        return jsonify({"error": "Task and due date are required"}), 400

    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (task, due_date, completed) VALUES (?, ?, ?)",
        (task, due_date, 0)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Task added successfully"}), 200

@app.route("/tasks")
def get_tasks():

    conn = get_db_connection()

    tasks = conn.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    conn.close()

    return jsonify([dict(task) for task in tasks])


# Complete task
@app.route("/complete_task/<int:task_id>", methods=["PUT"])
def complete_task(task_id):

    conn = get_db_connection()

    conn.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Task completed successfully"})


# Delete task
@app.route("/delete_task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Task deleted successfully"})

# Edit task
@app.route("/edit_task/<int:task_id>", methods=["PUT"])
def edit_task(task_id):

    data = request.get_json()

    new_task = data.get("task")

    if not new_task:
        return jsonify({"error": "Task is required"}), 400

    conn = get_db_connection()

    conn.execute(
        "UPDATE tasks SET task = ? WHERE id = ?",
        (new_task, task_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Task updated successfully"})

if __name__ == "__main__":
    create_table()
    app.run(host="0.0.0.0",port=5000)
