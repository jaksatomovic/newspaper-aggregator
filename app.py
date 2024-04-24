# app.py
from flask import Flask

app = Flask(__name__)

@app.route('/healthcheck')
def healthcheck():
    return 'Service is running', 200

if __name__ == '__app__':
    app.run(host='0.0.0.0', port=5000)
