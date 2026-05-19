from flask import Flask, render_template, request, redirect, session, jsonify, flash
import sqlite3
import os
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'tutor_booking_secret_2024'

# ========== DATABASE ==========
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tutors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        subject TEXT NOT NULL,
        bio TEXT,
        experience TEXT,
        rating REAL DEFAULT 5.0,
        price INTEGER DEFAULT 500,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT,
        student_email TEXT,
        tutor_id INTEGER,
        tutor_name TEXT,
        subject TEXT,
        date TEXT,
        time TEXT,
        status TEXT DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(tutor_id) REFERENCES tutors(id)
    )''')

    # Seed tutors
    c.execute("SELECT COUNT(*) FROM tutors")
    if c.fetchone()[0] == 0:
        tutors = [
            ('Rahul Sharma', 'rahul@tutor.com', hash_password('password123'), 'Mathematics', 'Expert in Algebra, Calculus and Statistics.', '5 years', 4.8, 600),
            ('Priya Patel', 'priya@tutor.com', hash_password('password123'), 'Physics', 'PhD in Physics, specializing in Mechanics.', '7 years', 4.9, 700),
            ('Arjun Nair', 'arjun@tutor.com', hash_password('password123'), 'English', 'Literature graduate with expertise in writing.', '4 years', 4.7, 500),
            ('Sneha Reddy', 'sneha@tutor.com', hash_password('password123'), 'Chemistry', 'Organic Chemistry specialist.', '6 years', 4.6, 650),
            ('Vikram Singh', 'vikram@tutor.com', hash_password('password123'), 'Computer Science', 'Software Engineer teaching Python and Web Dev.', '8 years', 5.0, 800),
            ('Meera Iyer', 'meera@tutor.com', hash_password('password123'), 'Biology', 'MSc Biology, passionate about science.', '3 years', 4.8, 550),
        ]
        c.executemany("INSERT INTO tutors(name,email,password,subject,bio,experience,rating,price) VALUES(?,?,?,?,?,?,?,?)", tutors)

    conn.commit()
    conn.close()

# ========== EMAIL ==========
def send_email(to_email, student_name, tutor_name, subject, date, time):
    try:
        sender = os.environ.get('EMAIL_USER', '')
        password = os.environ.get('EMAIL_PASS', '')
        if not sender or not password:
            return False

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Booking Confirmed - {subject} with {tutor_name}'
        msg['From'] = sender
        msg['To'] = to_email

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
            <div style="background:#7c3aed;padding:30px;text-align:center;border-radius:12px 12px 0 0;">
                <h1 style="color:white;margin:0;">Booking Confirmed! 🎉</h1>
            </div>
            <div style="background:#f9f9f9;padding:30px;border-radius:0 0 12px 12px;">
                <p>Hi <strong>{student_name}</strong>,</p>
                <p>Your session has been booked successfully!</p>
                <div style="background:white;padding:20px;border-radius:8px;border-left:4px solid #7c3aed;margin:20px 0;">
                    <p><strong>📚 Subject:</strong> {subject}</p>
                    <p><strong>👨‍🏫 Tutor:</strong> {tutor_name}</p>
                    <p><strong>📅 Date:</strong> {date}</p>
                    <p><strong>🕐 Time:</strong> {time}</p>
                </div>
                <p>Good luck with your session!</p>
            </div>
        </div>
        """
        msg.attach(MIMEText(html, 'html'))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender, password)
        server.sendmail(sender, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ========== HOME ==========
@app.route('/')
def home():
    conn = get_db()
    total_tutors = conn.execute("SELECT COUNT(*) FROM tutors").fetchone()[0]
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_bookings = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    top_tutors = conn.execute("SELECT * FROM tutors ORDER BY rating DESC LIMIT 3").fetchall()
    conn.close()
    return render_template('index.html', total_tutors=total_tutors,
                           total_students=total_students, total_bookings=total_bookings,
                           top_tutors=top_tutors)

# ========== AUTH ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        try:
            conn = get_db()
            conn.execute("INSERT INTO students(name,email,password) VALUES(?,?,?)", (name, email, password))
            conn.commit()
            conn.close()
            flash('Account created! Please login.', 'success')
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash('Email already registered!', 'error')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        role = request.form['role']
        conn = get_db()
        if role == 'student':
            user = conn.execute("SELECT * FROM students WHERE email=? AND password=?", (email, password)).fetchone()
            if user:
                session.update({'user_id': user['id'], 'user_name': user['name'],
                                'user_email': user['email'], 'role': 'student'})
                conn.close()
                return redirect('/student/dashboard')
        else:
            user = conn.execute("SELECT * FROM tutors WHERE email=? AND password=?", (email, password)).fetchone()
            if user:
                session.update({'user_id': user['id'], 'user_name': user['name'],
                                'user_email': user['email'], 'role': 'tutor'})
                conn.close()
                return redirect('/tutor/dashboard')
        conn.close()
        flash('Invalid email or password!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ========== TUTORS ==========
@app.route('/tutors')
def tutors():
    subject_filter = request.args.get('subject', '')
    search = request.args.get('search', '')
    conn = get_db()
    query = "SELECT * FROM tutors WHERE 1=1"
    params = []
    if subject_filter:
        query += " AND subject=?"
        params.append(subject_filter)
    if search:
        query += " AND (name LIKE ? OR subject LIKE ? OR bio LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    tutor_list = conn.execute(query, params).fetchall()
    subjects = conn.execute("SELECT DISTINCT subject FROM tutors ORDER BY subject").fetchall()
    conn.close()
    return render_template('tutors.html', tutors=tutor_list, subjects=subjects,
                           subject_filter=subject_filter, search=search)

# ========== BOOKING ==========
@app.route('/book/<int:tutor_id>', methods=['GET', 'POST'])
def book(tutor_id):
    if 'user_id' not in session or session.get('role') != 'student':
        flash('Please login as a student to book.', 'error')
        return redirect('/login')
    conn = get_db()
    tutor = conn.execute("SELECT * FROM tutors WHERE id=?", (tutor_id,)).fetchone()
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        conn.execute("""INSERT INTO bookings(student_id,student_name,student_email,tutor_id,tutor_name,subject,date,time)
                        VALUES(?,?,?,?,?,?,?,?)""",
                     (session['user_id'], session['user_name'], session['user_email'],
                      tutor_id, tutor['name'], tutor['subject'], date, time))
        conn.commit()
        conn.close()
        send_email(session['user_email'], session['user_name'], tutor['name'], tutor['subject'], date, time)
        flash(f'Booking confirmed with {tutor["name"]}!', 'success')
        return redirect('/student/dashboard')
    conn.close()
    return render_template('book.html', tutor=tutor)

# ========== STUDENT DASHBOARD ==========
@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('role') != 'student':
        return redirect('/login')
    conn = get_db()
    bookings = conn.execute("""SELECT b.*, t.rating, t.price, t.bio
                               FROM bookings b JOIN tutors t ON b.tutor_id=t.id
                               WHERE b.student_id=? ORDER BY b.created_at DESC""",
                            (session['user_id'],)).fetchall()
    total = len(bookings)
    pending = sum(1 for b in bookings if b['status'] == 'pending')
    confirmed = sum(1 for b in bookings if b['status'] == 'confirmed')
    conn.close()
    return render_template('student_dashboard.html', bookings=bookings,
                           total=total, pending=pending, confirmed=confirmed)

@app.route('/booking/cancel/<int:booking_id>')
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db()
    conn.execute("UPDATE bookings SET status='cancelled' WHERE id=? AND student_id=?",
                 (booking_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Booking cancelled.', 'success')
    return redirect('/student/dashboard')

# ========== TUTOR DASHBOARD ==========
@app.route('/tutor/dashboard')
def tutor_dashboard():
    if 'user_id' not in session or session.get('role') != 'tutor':
        return redirect('/login')
    conn = get_db()
    bookings = conn.execute("SELECT * FROM bookings WHERE tutor_id=? ORDER BY created_at DESC",
                            (session['user_id'],)).fetchall()
    total = len(bookings)
    pending = sum(1 for b in bookings if b['status'] == 'pending')
    confirmed = sum(1 for b in bookings if b['status'] == 'confirmed')
    earnings = confirmed * 500
    conn.close()
    return render_template('tutor_dashboard.html', bookings=bookings,
                           total=total, pending=pending, confirmed=confirmed, earnings=earnings)

@app.route('/booking/confirm/<int:booking_id>')
def confirm_booking(booking_id):
    if 'user_id' not in session or session.get('role') != 'tutor':
        return redirect('/login')
    conn = get_db()
    conn.execute("UPDATE bookings SET status='confirmed' WHERE id=? AND tutor_id=?",
                 (booking_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Booking confirmed!', 'success')
    return redirect('/tutor/dashboard')

@app.route('/booking/reject/<int:booking_id>')
def reject_booking(booking_id):
    if 'user_id' not in session or session.get('role') != 'tutor':
        return redirect('/login')
    conn = get_db()
    conn.execute("UPDATE bookings SET status='cancelled' WHERE id=? AND tutor_id=?",
                 (booking_id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Booking rejected.', 'success')
    return redirect('/tutor/dashboard')

import os
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
