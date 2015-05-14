from __future__ import absolute_import

from flask.ext.sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:tnwlEkfkdgo^7@221.143.42.85/lotto645'

db = SQLAlchemy(app)
