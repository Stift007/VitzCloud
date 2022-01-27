print("[VitzNode] Collecting Modules...")
import sqlite3
from flask import Flask, render_template,request
import os
from settings import *
from flask.helpers import send_from_directory, flash, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pycloudflare.abc import Settings
from pycloudflare.helpers import render, Traffic,secure_error,session
from pycloudflare.wrappers import Rule,FASS
from flask_dance.contrib.twitter import twitter, make_twitter_blueprint
from flask_dance.contrib.github import make_github_blueprint, github
from util import Badge, DiscordOAuth2, generate_badge
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user,login_required,current_user, logout_user
from werkzeug.utils import redirect
from random import choices
import util
from obscureql import DataBase
print("[VitzNode] Creating app  'Flask'...")
isStuck = False
Issue = ""
twitter_blueprint = make_twitter_blueprint("d6mD4DCxZoN9BZRN0uGU8i6bh","NWKQqSiimkg5umC3MvaC2mNnh0VhwCQVGVss5TxJRnY2tH5ya5",)

git_blueprint = make_github_blueprint("566095446331efc707f1",
"41b6dfc18a4b2dcff70c6078af06aad2d2a8c5df"
)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.register_blueprint(twitter_blueprint, url_prefix='/oauth_twitter')
app.register_blueprint(git_blueprint,url_prefix="/oauth_github")

print("[VitzNode] Setting up the CORS...")
CORS(app)
FASS(app)

print("[VitzNode] Connecting Database...")
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///users.db'
app.config["SECRET_KEY"] = APP_SECRET_KEY
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
    approved = db.Column(db.Integer())
    github_uri = db.Column(db.String(30),unique=True)
    twitter_uri = db.Column(db.String(30),unique=True)
    discord_username = db.Column(db.String(30))
    discord_userid = db.Column(db.Integer())

@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

print("[VitzNode] Creating Routes...")

@app.route("/admin/queue")
@login_required
def queue():
    engine = User.query.filter_by(approved=0)
    users = engine.all()
    if current_user.username in ['root','DS_Stift007']:
        return render_template("queuelist.html",users=users)

    return redirect("/error?errtype=401")

@app.route("/admin/approve")
@login_required
def approve_account():
    account = request.args.get('account')
    print(account)
    if current_user.username in ["DS_Stift007","root"]:
        db.session.execute(f"UPDATE user SET approved=1 WHERE username LIKE '{account}'")
        db.session.commit()
    return '<script>history.back()</script>'


@app.route("/admin/issue-error")
@login_required
def issue():
    if current_user.username in ["DS_Stift007","root"]:
        global isStuck
        global Issue
        isStuck = True
        Issue = request.args.get("issue")
        
    return '<script>history.back()</script>'


@app.route("/admin/delete")
@login_required
def decl_account():
    account = request.args.get('account')
    print(account)
    if current_user.username in ["DS_Stift007","root"]:
        db.session.execute(f"DELETE FROM user WHERE username LIKE '{account}'")
        db.session.commit()
    return '<script>history.back()</script>'

@app.route("/traffic-render")
def catch():
    session['CAUGHT'] = True
    traffic = Traffic(request)
    networking = Rule(Settings(
        on_error=secure_error
    ))
    traffic.network = networking
    session.store('trafficManager',traffic)
    return render()

@app.route('/')
def index():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    if not current_user.is_authenticated:
        return render_template("login.html")
    data = sqlite3.connect("users.db")
    data.cursor().execute("SELECT * FROM user;")
    users_db = data.cursor().fetchall()
    users = [User(username=i,bio=j,fullname=k,badges=l,courses=m,email=n,password=o) for i,j,k,l,m,n,o in users_db]
    for user in users:
        str_badges = user.badges
        user.badges_imgs = [generate_badge(i) for i in str_badges]
    return redirect("/@me")
    print(current_user.github_uri)

@app.route("/oauth/connect/discord")
def conn_disc():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    return redirect(util.DiscordOAuth2.discord_login_url)


@app.route("/callback/discord")
def callback():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    code = request.args.get("code")

    at = DiscordOAuth2.get_token(code)
    session["token"] = at
    obj = DiscordOAuth2.get_user(at)
    if not current_user.is_authenticated:
        user = User.query.filter_by (discord_userid=int(obj.get("id")))
        login_user(user)
        return redirect("/@me")
    username,userdis,userid = obj.get("username"),obj.get("discriminator"),obj.get("id")
    db.session.execute(f"UPDATE user SET discord_username='{username+'#'+userdis}', discord_userid={userid} WHERE username LIKE '{current_user.username}'")
    db.session.commit()
    return redirect("/@me")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','tiff','jfif','ico'}
@app.route("/logoff")
@login_required
def logoff():
    logout_user()
    return '<script>history.back()</script>'

@app.route('/callback/github')
def github_oauth():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    if not github.authorized:
        return redirect(url_for("github.login"))

    account_info = github.get("/user")

    if account_info.ok:
        acc_info_json = account_info.json()
        print(acc_info_json)
        print(acc_info_json['login'])
        db.session.execute(f"UPDATE user SET github_uri='{acc_info_json['login']}' WHERE username LIKE '{current_user.username}'")
        return redirect("/@me")
    return '''
    <meta http-equiv="refresh" content="3;url=/@me">
    <script>alert("Something went wron while authorizing the App :(")</script>
    '''


@app.route('/callback/twitter')
def twit_oauth():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    account_info = twitter.get("/account/settings")

    if account_info.ok:
        acc_info_json = account_info.json()
        print(acc_info_json)
        print(acc_info_json['screen_name'])
        db.session.execute(f"UPDATE user SET twitter_uri='{acc_info_json['screen_name']}' WHERE username LIKE '{current_user.username}'")
        return redirect("/@me")
    return '''
    <meta http-equiv="refresh" content="3;url=/@me">
    <script>alert("Something went wron while authorizing the App :(")</script>
    '''

@app.route("/account/config/avatar",methods=['POST'])
def update_avatar():
    
        if isStuck:
            return render_template('outages.html',outage=Issue)
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(current_user.username).lower()
            file.save(os.path.join("cdn/img", filename))
            return redirect(url_for('download_file', name=filename))
    
        return redirect("/@me")

@app.route("/settings",methods=['GET','POST'])
@login_required
def setng():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    print(current_user.username)
    if request.method == "POST":
        if request.form['NEW_BIO']:
            db.session.execute(f"UPDATE user SET bio='{request.form['NEW_BIO']}' WHERE username LIKE '{current_user.username}'")
            db.session.commit()
        print(request.files)
        if not request.files:
            print("AAAAAAAAA")
        if 'NEW_PFP' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['NEW_PFP']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print(file.filename)
            fn,fext = os.path.splitext(file.filename)
            filename = secure_filename(current_user.username).lower()
            file.save(os.path.join("cdn/img", filename+fext))
            return redirect(url_for('setng', name=filename+fext))
    

    engine = db.session.execute(f"SELECT * FROM user WHERE username LIKE '{current_user.username}'")
    data = engine.first()
    print(data)
    courses = data[5].split("|")

    return render_template("settings.html",crs=courses)

@app.route("/login", methods=['GET','POST'])
def logn():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['EMAIL'],password=request.form["PASSWORD"]).first()
        if not user:
            return redirect("/error?errtype=500")
        login_user(user)
        if not user.approved:
            return  render_template("inqueue.html")
        return redirect("/@me")

    return render_template("login.html")

@app.route("/error")
def error():
    return render_template("errno.html",err=request.args['errtype'])

@app.route("/@me")
@login_required
def rdr_me():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    return redirect(f"/profile/{current_user.username}")

@app.route("/profile/<username>")
def prf(username):
    if isStuck:
        return render_template('outages.html',outage=Issue)
    user = User.query.filter_by(username=username).first()
    str_badges = user.badges.split("|")
    badges = [generate_badge(i) for i in str_badges]
    print(user.discord_username is not "")
    return render_template("profile.html",username=username,badges=badges,user=user)



@app.route("/account/delete",methods=['GET','POST'])
def acc_del():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    if request.method == 'POST':
        user = User.query.filter_by(username=current_user.username)
        db.session.delete(user)
        db.session.commit()
        return redirect("/")
    return render_template("confirm.html")

@app.route("/register",methods=['GET','POST'])
def register():
    if isStuck:
        return render_template('outages.html',outage=Issue)
    if request.method == 'POST':
        user = User(
            username=secure_filename(request.form['username']),
            bio='No Bio set',
            fullname=request.form['fullname'],
            badges='Verifizierter Benutzer der ersten Stunde',
            courses='',
            email=request.form['email_addr'],
            approved=0,
            password=request.form['password'],
            discord_userid=000000,
            discord_username=None,
            github_uri=None
        )
        try:
            db.session.add(user)
            db.session.commit()
            login_user(user)
        except:
            return redirect("/error?errtype=500")
        if not user.approved:
            return  render_template("inqueue.html")
        return redirect("/@me")
    return render_template("register.html",rndm_name='-'.join(choices(util.random_names,k=2)))

@app.route("/cdn")
def sendCDN():
    fileID = request.args.get('f')
    print(fileID)
    return send_from_directory('cdn/admin-root',fileID)

@app.route("/cdn/<pth>/<fl>")
def cdn(pth,fl):
    return send_from_directory(f'cdn/{pth}',fl)

print("[VitzNode] Waiting for the CDN...")

if __name__ == "__main__":
    app.run(APP_HOST,80,debug=DEBUG)