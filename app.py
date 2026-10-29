from flask import Flask,render_template,request,redirect,session,send_from_directory,url_for
import os
import sqlite3

from database import init_db
from lip_extractor import extract_lips
from model import predict

app=Flask(__name__)
app.secret_key="secret123"

UPLOAD="uploads"

if not os.path.exists(UPLOAD):
    os.makedirs(UPLOAD)

init_db()

def db():
    return sqlite3.connect("database.db")


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        conn=db()
        cur=conn.cursor()

        cur.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (username,password)
        )

        conn.commit()

        return redirect("/")

    return render_template("register.html")


@app.route("/login",methods=["POST"])
def login():

    username=request.form["username"]
    password=request.form["password"]

    conn=db()
    cur=conn.cursor()

    cur.execute(
    "SELECT * FROM users WHERE username=? AND password=?",
    (username,password)
    )

    user=cur.fetchone()

    if user:
        session["user"]=username
        return redirect("/dashboard")

    return "Invalid Login"


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


@app.route("/predict",methods=["POST"])
def prediction():

    video=request.files["video"]

    path=os.path.join(UPLOAD,video.filename)
    video.save(path)

    frames=extract_lips(path)

    if len(frames)==0:
        result="No lips detected"
        confidence=0
    else:
        result,confidence=predict(frames)

    conn=db()
    cur=conn.cursor()

    cur.execute(
    "INSERT INTO predictions(username,result,confidence) VALUES(?,?,?)",
    (session["user"],result,confidence)
    )

    conn.commit()

    return render_template(
        "result.html",
        result=result,
        confidence=confidence,
        video=video.filename
    )


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD, filename)


@app.route("/history")
def history():

    conn=db()
    cur=conn.cursor()

    cur.execute(
    "SELECT result,confidence FROM predictions WHERE username=?",
    (session["user"],)
    )

    data=cur.fetchall()

    return render_template("history.html",data=data)


@app.route("/analytics")
def analytics():

    conn=db()
    cur=conn.cursor()

    cur.execute("SELECT result, COUNT(*) FROM predictions GROUP BY result")

    rows=cur.fetchall()

    labels=[r[0] for r in rows]
    values=[r[1] for r in rows]

    return render_template("analytics.html",labels=labels,values=values)


@app.route("/webcam")
def webcam():
    return render_template("webcam.html")


@app.route("/logout")
def logout():
    session.pop("user",None)
    return redirect("/")


if __name__=="__main__":
    app.run(debug=True)