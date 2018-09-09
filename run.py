from flask import Flask, render_template, send_from_directory
app = Flask(__name__)

@app.route("/")
def hello():
    return "used car project"

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.route('/a')
def a():
    return render_template('index.tmpl')


@app.route("/test", methods=["POST"])
def test():
    return _test(request.form["test"])


@app.route("/index")
def index():
    return _test("My Test Data")


if __name__ == "__main__":
    app.run(host='0.0.0.0', 
            debug=True)

