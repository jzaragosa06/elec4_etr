from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL


app = Flask(__name__)
app.secret_key = "123456"

# MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "flask_web_app_db"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)


@app.route("/")
def auth():
    return render_template("auth.html")


@app.route("/", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM users WHERE email = %s AND password = %s",
        (email, password),
    )
    data = cur.fetchone()
    cur.close()

    if data:
        # Assuming 'email' and 'password' are columns in your table
        if email == data["email"] and password == data["password"]:
            session["id"] = data["id"]
            return redirect(url_for("index"))

    return render_template("auth.html", error="Invalid Credentials")


@app.route("/user/profile")
def profile():
    if "id" in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (session["id"],))
        data = cur.fetchone()
        cur.close()
        return render_template("profile.html", user=data)
    return redirect(url_for("auth"))


@app.route("/user/update", methods=["POST"])
def update():
    if "id" in session:
        fname = request.form["fname"]
        lname = request.form["lname"]
        number = request.form["number"]
        address = request.form["address"]

        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE users SET fname = %s, lname = %s, number = %s, address = %s WHERE id = %s",
            (fname, lname, number, address, session["id"]),
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("profile"))
    return redirect(url_for("auth"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth"))


@app.route("/products")
def index():
    if "id" in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM products")
        data = cur.fetchall()
        cur.close()
        return render_template("index.html", products=data)
    return redirect(url_for("auth"))


@app.route("/products/add", methods=["POST"])
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        category = request.form["category"]
        status = request.form["status"]

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO products (name, description, price, stock, category, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, description, price, stock, category, status),
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("index"))


@app.route("/products/edit/<int:id>", methods=["POST"])
def edit_user(id):
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = float(request.form["price"])
        stock = int(request.form["stock"])
        category = request.form["category"]
        status = request.form["status"]
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE products SET name=%s, description=%s, price =%s, stock = %s, category = %s, status = %s WHERE id=%s",
            (name, description, price, stock, category, status, id),
        )
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("index"))


@app.route("/products/delete/<int:id>", methods=["POST"])
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
