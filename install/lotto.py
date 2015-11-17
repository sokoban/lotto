from flask import render_template,request, Flask, url_for, make_response,send_from_directory
from flask import session, g, redirect, abort, flash, _app_ctx_stack, json, jsonify
import os
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
from flask.ext import admin, login
from flask.ext.admin.contrib import sqla
from flask.ext.admin import helpers, expose
from flask.ext.admin import BaseView
import os.path as op
from flask.ext.admin.contrib.fileadmin import FileAdmin
from sqlite3 import dbapi2 as sqlite3
import string, random

app = Flask(__name__)

#app.config['DATABASE_FILE'] = 'sqlite_db.db'
#DATABASE = './sqlite_db.db'

# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

# Create in-memory database
#app.config['DATABASE_FILE'] = 'sqlite_db.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@221.143.42.85/lotto645'
#app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

@app.before_request
def before_request():
    g.user = None
    if 'userid' in session:
         print session['userid']


class genlottonumber(db.Model):
    seqno = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100))
    genmethod = db.Column(db.Integer)
    firstnum = db.Column(db.Integer)
    secondnum = db.Column(db.Integer)
    thirdnum = db.Column(db.Integer)
    fourthnum = db.Column(db.Integer)
    fifthnum = db.Column(db.Integer)
    sixthnum = db.Column(db.Integer)
    luckynum = db.Column(db.Integer)
    regdt = db.Column(db.DateTime)

    def __unicode__(self):
        return self.seqno

class Lottonumber(db.Model):
    lnumber = db.Column(db.Integer,primary_key=True)
    firstnum = db.Column(db.Integer)
    secondnum = db.Column(db.Integer)
    thirdnum = db.Column(db.Integer)
    fourthnum = db.Column(db.Integer)
    fifthnum = db.Column(db.Integer)
    sixthnum = db.Column(db.Integer)
    luckynum = db.Column(db.Integer)
    regdt = db.Column(db.DateTime)

    def __unicode__(self):
        return self.lnumber

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


def gennumber(name):
    lottonum = genlottonumber()
    lottonum.username = name

    lottonum = [4,7,23,24,35,37,9]
    return lottonum

@app.route('/sns')
def snspage():
   return render_template('sns.html')

@app.route('/')
def index():
    #db = get_db()
    #cur = db.execute('select title, text from entries order by id desc')
    #entries = cur.fetchall()

    resp = make_response(render_template('index.html'))
    resp.set_cookie('username','the username')

    return resp

@app.route('/header',methods=['GET'])
def headerpage():
    return render_template('header.html')

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    entry = Entries()
    entry.title = request.form['title']
    entry.text = request.form['text']
    db.session.add(entry)
    db.session.commit() 

    flash('New entry was successfully posted')
    return redirect(url_for('index'))

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

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

@app.route('/genlottonum')
def genlotto():
     
    ret = gennumber('test')
    if g.user:
        print g.user

    return jsonify(username = 'test',test='test') 

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

    #return render_template('login.html', error=error)
    flash(error)
    return redirect(url_for('index'))

@app.route('/displaynew')
def dispnews():
    


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('userid', None)
    flash('You were logged out')
    return redirect(url_for('index'))

@app.route('/error')
def errtest():
    abort(404)

@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp

#CSS File (Static File)
@app.route('/style/<path:filename>')
def send_foo(filename):
    return send_from_directory('./static/style/',filename)

@app.route('/static/<path:filename>')
def send_foo2(filename):
    return send_from_directory('./static/',filename)

if __name__ == '__main__':

    app_dir = os.path.realpath(os.path.dirname(__file__))
#    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
#    if not os.path.exists(database_path):
#        init_db()

    app.run(host='221.143.42.85',debug=True)
