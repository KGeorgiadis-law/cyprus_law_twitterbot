from flask import Flask
from flask import request
from CyprusLawBot import cyprusLawBot

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'GET':
    return "you should not be here..."
  else:
    # cyprusLawBot()
    return "hello!"