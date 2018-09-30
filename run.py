#!/usr/bin/env python

from flask import   Flask, render_template, send_from_directory, \
                    redirect, request, Response, stream_with_context, \
                    make_response, flash, url_for, send_from_directory
import os 
from dbapi.dbtools import Data_Getter

app = Flask(__name__)

@app.route("/")
@app.route("/index.html")
def index():
    return render_template('index.tmpl')


@app.route("/search", methods=["POST"])
def search():
    getter = Data_Getter()
    brand = request.form["brand"]
    model = request.form["model"]
    kmage = request.form["mileage"]
    year = request.form["age"]
    item = {'brand': brand, 'model': model, 'year': year, 'kmage': kmage}
    price = getter.get_price(item)
    return render_template("search.tmpl", model=item, price=price)


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

