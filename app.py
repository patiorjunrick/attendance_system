from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secretkey123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# ----------------- MODELS -----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    middle_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True, nullable=False)
    admission_number = db.Column(db.String(50), nullable=False)
    id_number = db.Column(db.String(50))
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50))
    email = db.Column(db.String(50))

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    day = db.Column(db.String(20))
    unit = db.Column(db.String(100))
    attending = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='attendances')

with app.app_context():
    db.create_all()

# School timetable units per day
units_by_day = {
    "Monday": [
        "E GOVERNMENT AND INSTITUTIONAL CHANGE",
        "SERVICE ORIENTED COMPUTING",
        "SOCIAL NETWORKING COMPUTING",
        "SOFTWARE ENGINEERING ",
        "SPECIAL TOPICS IN CONTEMPORARY ICTS "
    ],
    "Tuesday": [
        "USER INTERFACE PROGRAMMING",
        "SPECIAL TOPICS IN CONTEMPORARY ICTS ",
        "SERVICE ORIENTED COMPUTING",
        "ICT GROUP PROJECT "
    ],
    "Wednesday": [
        "E GOVERNMENT AND INSTITUTIONAL CHANGE",
        "USER INTERFACE PROGRAMMING",
        "NETWORK SYSTEMS INTERROGATION AND MAINTANANCE ",
        "SERVICE ORIENTED COMPUTING",
        "SOCIAL NETWORKING COMPUTING",
        "ICT GROUP PROJECT"
    ],
    "Thursday": [
        "NETWORK SYSTEMS INTERROGATION AND MAINTANANCE",
        "ICT GROUP PROJECT ",
        "USER INTERFACE PROGRAMMING",
        "SOCIAL NETWORKING COMPUTING"
    ],
    "Friday": [
        "SOFTWARE ENGINEERING ",
        "NETWORK SYSTEMS INTERROGATION AND MAINTANANCE ",
        "E GOVERNMENT AND INSTITUTIONAL CHANGE ",
        "SERVICE ORIENTED COMPUTING "
    ]
}
# ----------------- ROUTES -----------------

@app.route('/')
def home():
    return redirect(url_for('signup'))

# ---------------- SIGNUP -----------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match! Please try again."

        username = request.form['username']
        if User.query.filter_by(username=username).first():
            return "Username already exists! Please choose another."
        
        user = User(
            first_name=request.form['first_name'],
            middle_name=request.form['middle_name'],
            last_name=request.form.get('last_name'),
            username=username,
            admission_number=request.form['admission_number'],
            id_number=request.form.get('id_number'),
            password=generate_password_hash(password),
            phone=request.form.get('phone'),
            email=request.form.get('email')
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

# ---------------- LOGIN -----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        return "Invalid credentials!"
    return render_template('login.html')

# ---------------- DASHBOARD -----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    day = datetime.now().strftime("%A")  # Monday, Tuesday etc
    date = datetime.now().strftime("%d-%m-%Y")
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', day=day, date=date, user=user)


# ---------------- FILL ATTENDANCE -----------------
@app.route('/fill_attendance', methods=['GET', 'POST'])
def fill_attendance():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    day = datetime.now().strftime("%A")
    date = datetime.now().strftime("%d-%m-%Y")

    units = units_by_day.get(day, [])

    if request.method == 'POST':
        unit = request.form.get("unit")
        attending = request.form.get("attending")

        # Check if attendance already exists for this user/day/unit
        att = Attendance.query.filter_by(user_id=session['user_id'], day=day, unit=unit).first()
        if att:
            att.attending = attending  # Update existing
        else:
            att = Attendance(user_id=session['user_id'], day=day, unit=unit, attending=attending)
            db.session.add(att)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('fill_attendance.html', day=day, units=units)

#---------------- UNIT SELECTION -----------------------    
@app.route('/select_unit')
def select_unit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    day = datetime.now().strftime("%A")
    units = units_by_day.get(day, [])  # Only today's units

    return render_template('select_list.html', day=day, units=units)

# ---------------- ATTENDANCE LIST -----------------

@app.route('/attendance_list', methods=['GET'])
def attendance_list():
    unit = request.args.get('unit')
    day = datetime.now().strftime("%A")
    units = units_by_day.get(day, [])
    if not unit:
        records = []
    else:
        records = Attendance.query.filter_by(unit=unit).all()

    return render_template('attendance_list.html', records=records, units=units, selected_unit=unit)

# ---------------- LOGOUT -----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run