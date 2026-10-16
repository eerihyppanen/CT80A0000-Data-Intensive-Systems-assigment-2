"""A small Flask app for viewing and changing three SQLite databases."""

import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)
DATA_DIR = Path(__file__).parent / "data"

# Each option uses its own database file and one small table.
DATABASES = {
    "students": {
        "title": "Students",
        "columns": ("name", "email"),
        "labels": ("Student name", "Email"),
        "types": ("text", "email"),
        "sample": [
            ("Anna Laine", "anna@example.com"),
            ("Mika Virtanen", "mika@example.com"),
            ("Sara Niemi", "sara@example.com"),
            ("Leo Korhonen", "leo@example.com"),
            ("Emma Salmi", "emma@example.com"),
        ],
    },
    "courses": {
        "title": "Courses",
        "columns": ("title", "credits"),
        "labels": ("Course title", "Credits"),
        "types": ("text", "number"),
        "sample": [
            ("Introduction to Python", 5),
            ("Database Basics", 5),
            ("Web Development", 5),
            ("Computer Networks", 3),
            ("Software Project", 10),
        ],
    },
    "library": {
        "title": "Library",
        "columns": ("title", "author"),
        "labels": ("Book title", "Author"),
        "types": ("text", "text"),
        "sample": [
            ("Python Basics", "Alex Smith"),
            ("Learning SQL", "Jamie Brown"),
            ("Simple Websites", "Taylor Green"),
            ("Understanding Networks", "Morgan Lee"),
            ("Everyday Programming", "Casey Jones"),
        ],
    },
}


def init_databases():
    
    DATA_DIR.mkdir(exist_ok=True)
    for name, config in DATABASES.items():
        with closing(sqlite3.connect(DATA_DIR / f"{name}.db")) as db:
            exists = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='records'"
            ).fetchone()
            if exists:
                continue  # Keep existing changes, even if all rows were deleted.
            first, second = config["columns"]
            second_type = "INTEGER" if name == "courses" else "TEXT"
            db.execute(
                f"CREATE TABLE records (id INTEGER PRIMARY KEY, "
                f"{first} TEXT NOT NULL, {second} {second_type} NOT NULL)"
            )
            db.executemany(
                f"INSERT INTO records ({first}, {second}) VALUES (?, ?)",
                config["sample"],
            )
            db.commit()


@app.route("/", methods=["GET", "POST"])
def index():
    selected = request.args.get("database", "students")
    if selected not in DATABASES:
        abort(404)
    config = DATABASES[selected]
    first, second = config["columns"]
    error = None
    editing = None
    values = ("", "")

    with closing(sqlite3.connect(DATA_DIR / f"{selected}.db")) as db:
        if request.method == "POST":
            action = request.form.get("action")
            record_id = request.form.get("id", type=int)
            if action not in ("add", "update", "delete"):
                abort(400)
            if action in ("update", "delete"):
                editing = db.execute(
                    "SELECT * FROM records WHERE id = ?", (record_id,)
                ).fetchone()
                if editing is None:
                    abort(404)
            if action == "delete":
                db.execute("DELETE FROM records WHERE id = ?", (record_id,))
            else:
                values = (request.form.get("first", "").strip(),
                          request.form.get("second", "").strip())
                if not all(values):
                    error = "Please fill in both fields."
                elif any(len(value) > 100 for value in values):
                    error = "Each field must contain at most 100 characters."
                elif selected == "courses" and (
                    not values[1].isascii() or not values[1].isdigit()
                    or not 1 <= int(values[1]) <= 30
                ):
                    error = "Credits must be a whole number between 1 and 30."
                elif selected == "students" and (
                    "@" not in values[1] or not all(values[1].split("@", 1))
                ):
                    error = "Please enter an email address."
                if error is None:
                    # Column names come only from DATABASES user values use placeholders.
                    if action == "add":
                        db.execute(
                            f"INSERT INTO records ({first}, {second}) VALUES (?, ?)",
                            values,
                        )
                    else:
                        db.execute(
                            f"UPDATE records SET {first} = ?, {second} = ? WHERE id = ?",
                            (*values, record_id),
                        )
            if error is None:
                db.commit()
                return redirect(url_for("index", database=selected))
        elif "edit" in request.args:
            editing = db.execute(
                "SELECT * FROM records WHERE id = ?",
                (request.args.get("edit", type=int),),
            ).fetchone()
            if editing is None:
                abort(404)
            values = editing[1:]

        rows = db.execute("SELECT * FROM records ORDER BY id").fetchall()

    return render_template(
        "index.html", databases=DATABASES, selected=selected, config=config,
        rows=rows, editing=editing, values=values, error=error,
    )


if __name__ == "__main__":
    init_databases()
    app.run(host="127.0.0.1", port=5000)
