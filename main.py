from flask import Flask
from flask import request

from Cyprus+Law+Bot import CyprusLawBot

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def run_bot():

  if request.method == 'POST':
    CyprusLawBot()
    return ""
  elif request.method == 'GET':
    return "hello there!"
