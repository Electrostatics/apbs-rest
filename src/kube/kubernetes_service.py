from flask import Flask

try:
    import simplejson as json
except:
    import json

app = Flask(__name__)



if __name__ == '__main__':
    app.run()