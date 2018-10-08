#!/usr/bin/env python

from flask import   Flask, render_template, send_from_directory, \
                    redirect, request, Response, stream_with_context, \
                    make_response, flash, url_for, send_from_directory
import os 
from dbapi.dbtools import Data_Getter

# api versioning
#from api.v1 import api as api_v1
#from api import common

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
@app.route("/index.html", methods=["GET", "POST"])
def index():
    getter = Data_Getter()

    if request.method == 'POST':
        print('POST start')
        brand = request.form["brand"]
        print(brand)
    else:
        print('GET start')
        brands = getter.get_brands()
        #
        #
        # name = request.form.get('name', None)
        # if name is None:
        #
        #
        #brand = request.form['brand']
        brand = request.args.get('brand', None)

        if brand is None:
            return render_template('index.tmpl', brands=brands)
        else:
            print('GET model')
            models = getter.get_models(brand)
            print(models)
            return render_template('index.tmpl', brands=brands, models=models)

    return render_template('index.tmpl',brands=brands)

@app.route("/search", methods=["POST"])
@app.route("/search", methods=["POST"])
def search():
    getter = Data_Getter()
    brand = request.form["brand"]
    model = request.form["model"]
    kmage = request.form["mileage"]
    year = request.form["age"]
    item = {'brand': brand, 'model': model, 'year': year, 'kmage': kmage}
    price = getter.get_price(item)
    print(item)
    return render_template("search.tmpl", model=item, price=price)


@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

