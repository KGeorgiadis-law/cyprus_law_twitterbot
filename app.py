from flask import Flask
from flask import request
from CyprusLawBot import CyprusLawBot

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    return "hello there!"
  else:
    CyprusLawBot()
    return ""