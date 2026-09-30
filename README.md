# Flask To-Do List

A simple Flask to-do list with SQLite storage. Add, edit, and delete tasks; they stay saved between runs.

## Run locally

1. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install Flask and start the app:

   ```powershell
   python -m pip install -r requirements.txt
   python app.py
   ```

3. Open http://127.0.0.1:5000.

The SQLite database is created automatically in `instance/todo.sqlite3`. For deployment, set a private `SECRET_KEY` environment variable and turn off Flask debug mode.
