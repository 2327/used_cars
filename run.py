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
    return render_template('a.tmpl')

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

#@app.route('/<string:page_name>/')
#def static_page(page_name):
#    return render_template('%s.html' % page_name)

if __name__ == "__main__":
    app.run(host='0.0.0.0', 
            debug=True)