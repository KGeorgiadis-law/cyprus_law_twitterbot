from flask import Flask
from flask import request
from CyprusLawBot import cyprusLawBot
from os import getenv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Etag(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  etag = db.Column(db.String(80))

  def __repr__(self):
    return self.etag

class Tweet(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  tweet_text = db.Column(db.String(200))

  def __repr__(self):
    return self.tweet_text

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    return "you should not be here..."
  else:
    # cyprusLawBot()
    return "running..."