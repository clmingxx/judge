from markupsafe import escape
from flask import Flask, render_template, render_template, request

app = Flask(__name__, static_folder = 'static')

# @app.route('/')
# def hello_world():
#     return 'Hello, World!'

@app.route("/<name>")
def hello(name):
    return f"Hello, {escape(name)}!"

@app.route('/')
def hello_world():
    return render_template('index.html')

if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(debug=True)