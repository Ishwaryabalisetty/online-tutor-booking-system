from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        tutor_name TEXT,
        subject TEXT
    )
    ''')

    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']

        conn = sqlite3.connect('database.db')
        conn.execute("INSERT INTO students(name,email) VALUES(?,?)",(name,email))
        conn.commit()
        conn.close()

        return redirect('/tutors')

    return render_template("register.html")


@app.route('/tutors')
def tutors():
    tutor_list = [
        {"name":"Rahul","subject":"Mathematics"},
        {"name":"Priya","subject":"Physics"},
        {"name":"Arjun","subject":"English"}
    ]

    return render_template("tutors.html", tutors=tutor_list)


@app.route('/book', methods=['POST'])
def book():
    student = request.form['student']
    tutor = request.form['tutor']
    subject = request.form['subject']

    conn = sqlite3.connect('database.db')
    conn.execute("INSERT INTO bookings(student_name,tutor_name,subject) VALUES(?,?,?)",(student,tutor,subject))
    conn.commit()
    conn.close()

    return render_template("booking.html", student=student, tutor=tutor)


if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=int(__import__('os').environ.get('PORT', 5000)), debug=False)