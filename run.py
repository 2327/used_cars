from flask import   Flask, render_template, send_from_directory, \
                    redirect, request, Response, stream_with_context, \
                    make_response, flash, url_for, send_from_directory

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.tmpl')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')


@app.route("/test", methods=["POST"])
def test():
    return _test(request.form["test"])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)

