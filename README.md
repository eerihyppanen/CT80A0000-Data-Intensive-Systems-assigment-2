# University Database Manager

A simple Python and Flask web app with three SQLite databases.
Select a database and click **Open** to view, add, edit, or delete records.


### Setup and how to run

Install Python 3.10 or newer, then open a terminal in this folder:

```powershell
python -m pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in your browser. Keep the terminal open while using the app. Press Ctrl+C to stop it.

## Databases

The first run creates these files automatically, with five dummy records each:

| File | Fields in the records table |
| --- | --- |
| `data/students.db` | id, name, email |
| `data/courses.db` | id, title, credits |
| `data/library.db` | id, title, author |

Each database has one table called `records`. Changes are saved automatically
and remain after restarting the app.
