from flask import render_template,request, Flask, url_for, make_response,send_from_directory
from flask import session, g, redirect, abort, flash, _app_ctx_stack, json, jsonify
import os
from flask.ext.sqlalchemy import SQLAlchemy, Pagination
from flaskext.mysql import MySQL
from wtforms import form, fields, validators
from flask.ext import admin, login
from flask.ext.admin.contrib import sqla
from flask.ext.admin import helpers, expose
from flask.ext.admin import BaseView
import os.path as op
from flask.ext.admin.contrib.fileadmin import FileAdmin
from sqlite3 import dbapi2 as sqlite3
import string, random
from utils.pagination import Pagination
from sqlalchemy import func, text
import utils.wordpro 

app = Flask(__name__)

#mysql = MySQL()
app.config['SECRET_KEY'] = '123456790'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'lotto645'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://'
#mysql.init_app(app)

db = SQLAlchemy(app)

class Newsfeeds(db.Model):
    __tablename__ = "newsfeeds"

    seqno = db.Column(db.Integer, primary_key=True)
    newstitle = db.Column(db.String(500))
    uriaddr = db.Column(db.String(500))
    sitename = db.Column(db.String(300))
    description = db.Column(db.Text)
    regdt = db.Column(db.DateTime)
    publisheddate = db.Column(db.DateTime)
    titlecategory = db.Column(db.String(100))
    alertflag = db.Column(db.Integer)
    testfield = db.Text

    def __init__(self, newstitle=None,uriaddr=None, sitename=None, description=None, regdt=None, publisheddate=None, titlecategory=None, alertflag=None):
        self.newstitle = newstitle
        self.sitename = sitename
        self.description = description
        self.regdt = regdt
        self.publisheddate = publisheddate
        self.titlecategory = titlecategory
        self.alertflag = alertflag

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username

@app.before_request
def before_request():
    g.user = None
    if 'userid' in session:
         print session['userid']

def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

#CSS File (Static File)
@app.route('/style/<path:filename>')
def send_foo(filename):
    return send_from_directory('./static/style/',filename)

@app.route('/static/<path:filename>')
def send_foo2(filename):
    return send_from_directory('./static/',filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registers the user."""
    if g.user:
        return redirect(url_for('timeline'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or \
                 '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        elif get_user_id(request.form['username']) is not None:
            error = 'The username is already taken'
        else:
            g.db.execute('''insert into user (
                username, email, pw_hash) values (?, ?, ?)''',
                [request.form['username'], request.form['email'],
                 generate_password_hash(request.form['password'])])
            g.db.commit()
            flash('You were successfully registered and can login now')


            return redirect(url_for('login'))
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        users = db.session.query(User)
        username = request.form['username']
        password = request.form['password']

        users = db.session.query(User).filter_by(username=username).first()
        passwords = db.session.query(User).filter_by(password=password).first() 

        if users is None:
            error = 'Invalid username'
        elif passwords is None:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['userid'] = users.username
            flash('You were logged in')
            return redirect(url_for('index'))

    return render_template('login.html', error=error)
    #flash(error)
    #return redirect(url_for('index'))


@app.route("/test")
def test():
    return render_template('test.html') 

@app.route("/wordpro/")
@app.route("/wordpro/<int:page>")
def wordprocess(page=1):
    pagenum = request.args.get('page')
    if pagenum:
        page = int(request.args.get('page'))
    category = request.args.get('category')

    count = db.session.query(func.count('*')).select_from(Newsfeeds).filter(Newsfeeds.newstitle.like('cve%')).scalar()

    news = Newsfeeds.query.filter(Newsfeeds.newstitle.like('cve%')).order_by(Newsfeeds.seqno.desc()).limit(10).offset(page).all()
    for a in news:
        a.testfield = utils.wordpro.ie_preprocess(a.description) 

    if not news and page !=1:
        abort(404)
    pagination = Pagination(page, 10, count)

    return render_template('wordpro.html', pagination=pagination,news=news ) 


@app.route("/")
@app.route("/<int:page>/<category>")
def index(page=1,category=None):
    
    pagenum = request.args.get('page')
    if pagenum:
        page = int(request.args.get('page'))

    category = request.args.get('category')

    if category:
        print category + '%' 
        count = db.session.query(func.count('*')).select_from(Newsfeeds).filter(Newsfeeds.newstitle.like('cve%')).scalar()
        news = Newsfeeds.query.filter(Newsfeeds.newstitle.like('cve%')).order_by(Newsfeeds.seqno.desc()).limit(10).offset(page).all()
    else:
        count = db.session.query(func.count('*')).select_from(Newsfeeds).scalar()
        news = Newsfeeds.query.order_by(Newsfeeds.seqno.desc()).limit(10).offset(page).all()

    #count = db.session.query(func.count('*')).select_from(Newsfeeds).scalar()
    #news = Newsfeeds.query.order_by(Newsfeeds.seqno.desc()).limit(10).offset(page).all()

    if not news and page !=1:
        abort(404)
    pagination = Pagination(page, 10, count)

    return render_template('index.html', pagination=pagination,news=news ) 

if __name__ == '__main__':
    app_dir = os.path.realpath(os.path.dirname(__file__))
    app.run(host='221.143.42.85',debug=True)
