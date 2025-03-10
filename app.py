from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key"  # Important for flash messages

# Database setup (SQLite for simplicity)
DATABASE = "hiring_portal.db"

def create_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            position TEXT NOT NULL,
            resume_path TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()  # Ensure table exists on startup

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

@app.route("/")
def index():
    conn = get_db_connection()
    applicants = conn.execute("SELECT * FROM applicants").fetchall()
    conn.close()
    return render_template("index.html", applicants=applicants)

@app.route("/apply", methods=["GET", "POST"])
def apply():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        position = request.form["position"]
        resume = request.files["resume"]

        if resume:
            resume_path = f"resumes/{resume.filename}" #create a folder called "resumes" in your project directory.
            resume.save(resume_path)

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO applicants (name, email, phone, position, resume_path)
                    VALUES (?, ?, ?, ?, ?)
                """, (name, email, phone, position, resume_path))
                conn.commit()
                flash("Application submitted successfully!", "success")
            except sqlite3.IntegrityError:
                flash("Email already registered.", "error")

            conn.close()
            return redirect(url_for("index"))
        else:
            flash("Please upload a resume.", "error")
            return render_template("apply.html")

    return render_template("apply.html")

@app.route("/applicant/<int:applicant_id>")
def applicant_details(applicant_id):
    conn = get_db_connection()
    applicant = conn.execute("SELECT * FROM applicants WHERE id = ?", (applicant_id,)).fetchone()
    conn.close()
    if applicant:
        return render_template("applicant_details.html", applicant=applicant)
    else:
        flash("Applicant not found.", "error")
        return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True) #remove debug=True in production.
