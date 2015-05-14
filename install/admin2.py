import os
from flask import Flask, url_for, redirect, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from wtforms import form, fields, validators
from flask.ext import admin, login
from flask.ext.admin.contrib import sqla
from flask.ext.admin import helpers, expose
from flask.ext.admin import BaseView

# Create Flask application
app = Flask(__name__)


# Create dummy secrey key so we can use sessions
app.config['SECRET_KEY'] = '123456790'

#MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:tnwlEkfkdgo^7@221.143.42.85/lotto645'
db = SQLAlchemy(app)

# SQLite
# Create in-memory database
#app.config['DATABASE_FILE'] = 'sample_db.sqlite'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
#app.config['SQLALCHEMY_ECHO'] = True
#db = SQLAlchemy(app)


# Create user model. For simplicity, it will store passwords in plain text.
# Obviously that's not right thing to do in real world application.

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
    login = db.Column(db.String(80), unique=True)
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


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated()


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))

class BookAdmin(sqla.ModelView):
    column_display_pk = False
    form_columns = ['bookname','author','publisher','description','publishdate']

class LottoAdmin(sqla.ModelView):
    column_display_pk = False
    form_columns = ['lnumber','firstnum','secondnum','thirdnum','fourthnum','fifthnum','sixthnum','luckynum','regdt']

class GenLottoAdmin(sqla.ModelView):
    column_display_pk = False
    form_columns = ['username','genmethod','firstnum','secondnum','thirdnum','fourthnum','fifthnum','sixthnum','luckynum','regdt']

# Flask views
@app.route('/')
def index():
    return render_template('index.html')

# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, 'Auth', index_view=MyAdminIndexView(), base_template='my_master.html')

# Add view
admin.add_view(MyModelView(User, db.session))
admin.add_view(LottoAdmin(Lottonumber, db.session))
admin.add_view(GenLottoAdmin(genlottonumber, db.session))

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    #database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])

    # Start app
    app.run(host='221.143.42.85',debug=True)
