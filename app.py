print("[VitzNode] Collecting Modules...")
from flask import Flask, render_template,request
from flask.helpers import send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from env.pycloudflare.helpers import render
from util import Badge, generate_badge
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user,login_required,current_user, logout_user
from werkzeug.utils import redirect
from random import choices
import util
from obscureql import DataBase
print("[VitzNode] Creating app  'Flask'...")

app = Flask(__name__)
print("[VitzNode] Setting up the CORS...")
CORS(app)

print("[VitzNode] Connecting Database...")
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SECRET_KEY"] = 'VITZNODE'
db = SQLAlchemy(app)
sql = DataBase('users.db')
print("[VitzNode] Creating User Manager...")
loginManager = LoginManager()
loginManager.init_app(app)

print("[VitzNode] Creating Objects...")
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30),unique=True)
    bio = db.Column(db.String(30))
    fullname = db.Column(db.String(30),unique=True)
    badges = db.Column(db.String(1000))
    courses = db.Column(db.String(1000))
    email = db.Column(db.String(30),unique=True)
    password = db.Column(db.String(30))

@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

print("[VitzNode] Creating Routes...")

@app.route('/')
def index():
    if not current_user.is_authenticated:
        return render_template("login.html")
    
    engine = db.session.execute("SELECT * FROM user;")
    db.session.commit()
    users = engine.all()
    for user in users:
        str_badges = user.badges
        user.badges_imgs = [generate_badge(i) for i in str_badges]
    return render_template("userlist.ejs",users=users)

@app.route("/logoff")
@login_required
def logoff():
    logout_user()
    return '<script>history.back()</script>'

@app.route("/settings",methods=['GET','POST'])
@login_required
def setng():
    print(current_user.username)
    if request.method == "POST":
        if request.form['NEW_BIO']:
            db.session.execute(f"UPDATE user SET bio='{request.form['NEW_BIO']}' WHERE username LIKE '{current_user.username}'")
            db.session.commit()

    engine = db.session.execute(f"SELECT * FROM user WHERE username LIKE '{current_user.username}'")
    data = engine.first()
    print(data)
    courses = data[5].split("|")

    return render_template("settings.html",crs=courses)

@app.route("/login", methods=['GET','POST'])
def logn():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['EMAIL'],password=request.form["PASSWORD"]).first()
        if not user:
            return redirect("/error?errtype=500")
        login_user(user)
        return redirect("/@me")
    return render_template("login.html")

@app.route("/error")
def error():
    return render_template("errno.html",err=request.args['errtype'])

@app.route("/@me")
@login_required
def rdr_me():
    return redirect(f"/profile/{current_user.username}")

@app.route("/profile/<username>")
def prf(username):
    user = User.query.filter_by(username=username).first()
    str_badges = user.badges.split("|")
    badges = [generate_badge(i) for i in str_badges]
    return render_template("profile.html",username=username,badges=badges,user=user)



@app.route("/account/delete",methods=['GET','POST'])
def acc_del():
    if request.method == 'POST':
        user = User.query.filter_by(username=current_user.username)
        db.session.delete(user)
        db.session.commit()
        return redirect("/")
    return render_template("confirm.html")

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=secure_filename(request.form['username']),
            bio='No Bio set',
            fullname=request.form['fullname'],
            badges='Verifizierter Benutzer der ersten Stunde',
            courses='',
            email=request.form['email_addr'],
            password=request.form['password']
        )
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
        except:
            return redirect("/error?errtype=500")
        return redirect("/@me")
    return render_template("register.html",rndm_name='-'.join(choices(util.random_names,k=2)))

@app.route("/cdn/<pth>/<fl>")
def cdn(pth,fl):
    return send_from_directory(f'cdn/{pth}',fl)

print("[VitzNode] Waiting for the CDN...")

if __name__ == "__main__":
    app.run(debug=True)