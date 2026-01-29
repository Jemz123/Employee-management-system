from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------- HOME PAGE ----------\
@app.route("/")
def home():
    return render_template("home.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials", "danger")
    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username,password,role) VALUES (%s,%s,%s)",
                           (username, hashed_password, role))
            conn.commit()
            flash("Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except:
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))
        finally:
            cursor.close()
            conn.close()

    return render_template("register.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("dashboard.html", employees=employees, role=session['role'])

# ---------- ADD EMPLOYEE ----------
@app.route("/add", methods=["GET","POST"])
def add_employee():
    if 'username' not in session or session['role'] != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        department = request.form['department']
        salary = request.form['salary']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employees (name,email,position,department,salary) VALUES (%s,%s,%s,%s,%s)",
            (name,email,position,department,salary)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Employee added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template("add_employee.html")

# ---------- EDIT EMPLOYEE ----------
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit_employee(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    employee = cursor.fetchone()

    if not employee:
        flash("Employee not found!", "danger")
        return redirect(url_for('dashboard'))

    if session['role'] == 'user' and employee['id'] != session['user_id']:
        flash("You can only edit your own info!", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        department = request.form['department']
        salary = request.form['salary']

        cursor.execute(
            "UPDATE employees SET name=%s,email=%s,position=%s,department=%s,salary=%s WHERE id=%s",
            (name,email,position,department,salary,id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Employee updated successfully!", "success")
        return redirect(url_for('dashboard'))

    cursor.close()
    conn.close()
    return render_template("edit_employee.html", employee=employee)

# ---------- DELETE EMPLOYEE ----------
@app.route("/delete/<int:id>")
def delete_employee(id):
    if 'username' not in session or session['role'] != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Employee deleted successfully!", "success")
    return redirect(url_for('dashboard'))

# ---------- VIEW EMPLOYEE ----------
@app.route("/view/<int:id>")
def view_employee(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
    employee = cursor.fetchone()
    cursor.close()
    conn.close()

    if not employee:
        flash("Employee not found!", "danger")
        return redirect(url_for('dashboard'))

    return render_template("view_employee.html", employee=employee)

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
