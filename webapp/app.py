from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
import sqlite3
import base64, os, sys

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

DB_FILE = os.environ.get('DB_FILE', '/tmp/1publiccomplaintdb.db')


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# Initialize database
with app.app_context():
    conn = get_db_connection()
    with open('init_db.sql', 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/AdminLogin')
def AdminLogin():
    return render_template('AdminLogin.html')


@app.route('/OfficerLogin')
def OfficerLogin():
    return render_template('OfficerLogin.html')


@app.route('/UserLogin')
def UserLogin():
    return render_template('UserLogin.html')


@app.route('/NewOfficer')
def NewOfficer():
    return render_template('NewOfficer.html')


@app.route('/NewUser')
def NewUser():
    return render_template('NewUser.html')


@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM officertb ")
            data = cur.fetchall()

            return render_template('AdminHome.html', data=data)

        else:
            flash('Username or Password is wrong')
            return render_template('AdminLogin.html')


@app.route("/AdminHome")
def AdminHome():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM officertb ")
    data = cur.fetchall()

    return render_template('AdminHome.html', data=data)


@app.route("/AUserInfo")
def AUserInfo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb ")
    data = cur.fetchall()
    return render_template('AUserInfo.html', data=data)


@app.route("/newofficer", methods=['GET', 'POST'])
def newofficer():
    if request.method == 'POST':
        uname = request.form['uname']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']
        depart = request.form['depart']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * from officertb where username=?", (username,))
        data = cursor.fetchone()
        if data is None:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO officertb VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)", (uname, mobile, email, address, depart, username, password))
            conn.commit()
            conn.close()

            flash('Record Saved!')
            return render_template('NewOfficer.html')
        else:
            flash('Already Register This  Officer Name!')
            return render_template('NewOwner.html')


@app.route("/officerlogin", methods=['GET', 'POST'])
def officerlogin():
    if request.method == 'POST':

        username = request.form['uname']
        password = request.form['password']
        session['oname'] = request.form['uname']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * from officertb where username=? and Password=?", (username, password))
        data = cursor.fetchone()
        if data is None:

            flash('Username or Password is wrong')
            return render_template('OfficerLogin.html')

        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM officertb where username=?", (session['oname'],))
            data1 = cur.fetchall()
            return render_template('OfficerHome.html', data=data1)


@app.route('/OfficerHome')
def OfficerHome():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM officertb where username=?", (session['oname'],))
    data1 = cur.fetchall()
    return render_template('OfficerHome.html', data=data1)


@app.route('/OUserInfo')
def OUserInfo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb")
    data = cur.fetchall()

    return render_template('OUserInfo.html', data=data)


@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        uname = request.form['uname']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username=?", (username,))
        data = cursor.fetchone()
        if data is None:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO regtb VALUES (NULL, ?, ?, ?, ?, ?, ?)", (uname, mobile, email, address, username, password))
            conn.commit()
            conn.close()

            flash('Record Saved!')

            return render_template('NewUser.html')
        else:
            flash('Already Register This  UserName!')
            return render_template('NewUser.html')


@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':

        username = request.form['uname']
        password = request.form['password']

        session['uname'] = request.form['uname']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * from regtb where username=? and Password=?", (username, password))
        data = cursor.fetchone()
        if data is None:

            flash('Username or Password is wrong')
            return render_template('UserLogin.html')

        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM regtb where username=?", (session['uname'],))
            data1 = cur.fetchall()
            return render_template('UserHome.html', data=data1)


@app.route('/UserHome')
def UserHome():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM regtb where username=?", (session['uname'],))
    data1 = cur.fetchall()
    return render_template('UserHome.html', data=data1)


@app.route('/NewComplaint', methods=['GET', 'POST'])
def NewComplaint():
    if request.method == 'POST':
        location = request.form['location']
        complaintinfo = request.form['complaintinfo']
        ctype = request.form['ctype']
        # For now, no image upload, set to empty
        image = ''
        image1 = ''
        from datetime import datetime
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = 'Pending'
        ans = ''
        officername = ''  # To be assigned later

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO complainttb (UserName, Location, ComplaintInfo, Image, Date, Status, Type, Ans, Image1, OfficerName) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (session['uname'], location, complaintinfo, image, date, status, ctype, ans, image1, officername))
        conn.commit()
        conn.close()

        flash('Complaint Submitted!')
        return redirect(url_for('UserHome'))

    return render_template('NewComplaint.html')


@app.route('/UComplaintInfoInfo')
def UComplaintInfo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complainttb WHERE UserName=?", (session['uname'],))
    data = cur.fetchall()
    return render_template('UComplaintInfo.html', data=data)


@app.route('/OComplaintInfo')
def OComplaintInfo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complainttb WHERE OfficerName=?", (session['oname'],))
    data = cur.fetchall()
    return render_template('OComplaintInfo.html', data=data)


@app.route('/AComplaintInfo')
def AComplaintInfo():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM complainttb")
    data = cur.fetchall()
    return render_template('AComplaintInfo.html', data=data)


if __name__ == '__main__':
    # app.run(host='0.0.0.0', debug=True, port=5000)
    app.run(debug=True, use_reloader=True)
