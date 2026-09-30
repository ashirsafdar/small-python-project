import os
import sqlite3
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = Path(os.environ.get("INSTANCE_DIR", BASE_DIR / "instance"))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["DATABASE"] = INSTANCE_DIR / "todo.sqlite3"

INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(app.config["DATABASE"]) as connection:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


@app.get("/")
def index():
    tasks = get_db().execute(
        "SELECT * FROM tasks ORDER BY created_at, id"
    ).fetchall()
    return render_template(
        "index.html", tasks=tasks, editing_task=request.args.get("edit", type=int)
    )


@app.post("/add")
def add_task():
    title = request.form.get("title", "").strip()
    if not title:
        flash("Write a task before adding it.", "error")
    elif len(title) > 120:
        flash("Keep tasks to 120 characters or fewer.", "error")
    else:
        get_db().execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        get_db().commit()
    return redirect(url_for("index"))


@app.post("/edit/<int:task_id>")
def edit_task(task_id):
    title = request.form.get("title", "").strip()
    if not title:
        flash("Write a task before saving it.", "error")
    elif len(title) > 120:
        flash("Keep tasks to 120 characters or fewer.", "error")
    else:
        database = get_db()
        database.execute("UPDATE tasks SET title = ? WHERE id = ?", (title, task_id))
        database.commit()
    return redirect(url_for("index"))


@app.post("/toggle/<int:task_id>")
def toggle_task(task_id):
    database = get_db()
    database.execute(
        "UPDATE tasks SET completed = 1 - completed WHERE id = ?", (task_id,)
    )
    database.commit()
    return redirect(url_for("index", filter=request.form.get("filter", "all")))


@app.post("/delete/<int:task_id>")
def delete_task(task_id):
    database = get_db()
    database.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    database.commit()
    return redirect(url_for("index", filter=request.form.get("filter", "all")))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )
