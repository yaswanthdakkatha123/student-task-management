from flask import Flask, request, jsonify, render_template, session, redirect
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY",
    "student-task-manager-secret-key"
)


def get_db_connection():
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise Exception("DATABASE_URL is not set")

    return psycopg2.connect(database_url)


def create_table():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            due_date TEXT,
            due_time TEXT,
            user_id INTEGER
        )
    """)

    # Add due_time to existing tasks table if it doesn't exist
    cur.execute("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS due_time TEXT
    """)

    conn.commit()
    cur.close()
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
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
            """,
            (username, email, password)
        )

        conn.commit()

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.close()
        conn.close()

        return jsonify({
            "error": "Email already registered"
        }), 400

    cur.close()
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
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(
        """
        SELECT * FROM users
        WHERE email = %s AND password = %s
        """,
        (email, password)
    )

    user = cur.fetchone()

    cur.close()
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


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


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
    due_time = data.get("due_time")

    if not task or not due_date or not due_time:
        return jsonify({
            "error": "Task, due date and due time are required"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO tasks
        (task, due_date, due_time, completed, user_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (task, due_date, due_time, 0, session["user_id"])
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Task added successfully"
    }), 200


@app.route("/tasks")
def get_tasks():

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(
        """
        SELECT * FROM tasks
        WHERE user_id = %s
        ORDER BY id DESC
        """,
        (session["user_id"],)
    )

    tasks = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify(tasks)


@app.route("/complete_task/<int:task_id>", methods=["PUT"])
def complete_task(task_id):

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = %s AND user_id = %s
        """,
        (task_id, session["user_id"])
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Task completed successfully"
    })


@app.route("/delete_task/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM tasks
        WHERE id = %s AND user_id = %s
        """,
        (task_id, session["user_id"])
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Task deleted successfully"
    })


@app.route("/edit_task/<int:task_id>", methods=["PUT"])
def edit_task(task_id):

    if "user_id" not in session:
        return jsonify({
            "error": "Please login first"
        }), 401

    data = request.get_json()

    new_task = data.get("task")
    new_due_date = data.get("due_date")
    new_due_time = data.get("due_time")

    if not new_task or not new_due_date or not new_due_time:
        return jsonify({
            "error": "Task, due date and due time are required"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE tasks
        SET task = %s,
            due_date = %s,
            due_time = %s
        WHERE id = %s AND user_id = %s
        """,
        (
            new_task,
            new_due_date,
            new_due_time,
            task_id,
            session["user_id"]
        )
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "Task updated successfully"
    })


if __name__ == "__main__":
    create_table()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
