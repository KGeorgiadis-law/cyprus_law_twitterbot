from flask import Flask
from flask import request
from CyprusLawBot import cyprusLawBot
from os import getenv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
db = SQLAlchemy(app)

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(80), unique=True, nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)

  def __repr__(self):
      return '<User %r>' % self.username

class Etags(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  etag = db.Column(db.String(80))

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    return "you should not be here..."
  else:
    cyprusLawBot()
    return "running..."