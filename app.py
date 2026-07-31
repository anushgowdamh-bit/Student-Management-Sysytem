from flask import Flask, render_template, request, redirect, url_for, session
import psycopg as pg
import os
app = Flask(__name__)
app.secret_key = "sms123"

# PostgreSQL Connection
DATABASE_URL=os.environ.get("DATABASE_URL")
conn=pg.connect(DATABASE_URL)
cur = conn.cursor()

# ---------------- Login ----------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["user"] = username
            return redirect("/dashboard")
        else:
            return render_template("login.html", msg="Invalid Login")

    return render_template("login.html")


# ---------------- Dashboard ----------------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")


# ---------------- View Students ----------------

@app.route("/students")
def students():
    if "user" not in session:
        return redirect("/")

    cur.execute("SELECT * FROM students ORDER BY id")
    data = cur.fetchall()
    return render_template("students.html", students=data)


# ---------------- Add Student ----------------

@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        course = request.form["course"]
        email = request.form["email"]
        phone = request.form["phone"]

        cur.execute("""
        INSERT INTO students
        (name,age,gender,course,email,phone)
        VALUES(%s,%s,%s,%s,%s,%s)
        """,
        (name, age, gender, course, email, phone))

        conn.commit()

        return redirect("/students")

    return render_template("add.html")


# ---------------- Edit Student ----------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        course = request.form["course"]
        email = request.form["email"]
        phone = request.form["phone"]

        cur.execute("""
        UPDATE students
        SET name=%s,
            age=%s,
            gender=%s,
            course=%s,
            email=%s,
            phone=%s
        WHERE id=%s
        """,
        (name, age, gender, course, email, phone, id))

        conn.commit()

        return redirect("/students")

    cur.execute("SELECT * FROM students WHERE id=%s", (id,))
    student = cur.fetchone()

    return render_template("edit.html", student=student)


# ---------------- Delete Student ----------------

@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect("/")

    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()

    return redirect("/students")


# ---------------- Search ----------------

@app.route("/search", methods=["POST"])
def search():

    keyword = "%" + request.form["search"] + "%"

    cur.execute(
        "SELECT * FROM students WHERE name ILIKE %s ORDER BY id",
        (keyword,)
    )

    data = cur.fetchall()

    return render_template("students.html", students=data)


# ---------------- Logout ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
    app.run(debug=True)