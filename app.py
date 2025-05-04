
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize DB
def init_db():
    with sqlite3.connect("documents.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_name TEXT,
            doc_type TEXT,
            filename TEXT,
            expiry_date DATE
        )''')

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect("documents.db")
    cur = conn.cursor()

    # Handle file upload
    if request.method == "POST":
        staff_name = request.form["staff_name"]
        doc_type = request.form["doc_type"]
        expiry_date = request.form["expiry_date"]
        file = request.files["file"]

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            cur.execute("INSERT INTO documents (staff_name, doc_type, filename, expiry_date) VALUES (?, ?, ?, ?)",
                        (staff_name, doc_type, filename, expiry_date))
            conn.commit()
            return redirect(url_for("index"))

    # Handle search
    search = request.args.get("search", "")
    query = "SELECT * FROM documents WHERE staff_name LIKE ? OR doc_type LIKE ?"
    cur.execute(query, (f"%{search}%", f"%{search}%"))
    documents = cur.fetchall()

    # Filter expiring soon
    today = datetime.today().date()
    soon = today + timedelta(days=60)
    cur.execute("SELECT * FROM documents WHERE expiry_date <= ?", (soon,))
    expiring = cur.fetchall()

    conn.close()
    return render_template("index.html", documents=documents, expiring=expiring, search=search)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
