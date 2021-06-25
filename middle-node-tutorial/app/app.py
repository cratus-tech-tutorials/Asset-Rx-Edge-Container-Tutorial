import json

from flask import Flask, render_template
app = Flask(__name__)

@app.route("/get")
def get():
    response_data = {
        "message": "Hello world from Cratus!"}
    response = app.response_class(
        response=json.dumps(response_data),
        status=200,
        mimetype='application/json')
    return response

@app.route('/')
def root():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=8080)
