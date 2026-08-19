from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_table():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            due_date TEXT
        )
    """)

    # Existing database ki due_date column add cheyyadaniki
    columns = conn.execute("PRAGMA table_info(tasks)").fetchall()

    column_names = [column["name"] for column in columns]

    if "due_date" not in column_names:
        conn.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add_task", methods=["POST"])
def add_task():
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
    app.run(debug=True)