#!/usr/bin/env python

from flask import   Flask, render_template, send_from_directory, \
                    redirect, request, Response, stream_with_context, \
                    make_response, flash, url_for, send_from_directory, \
                    jsonify
import os, json
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
        brand = request.args.get('brand', None)

        if brand is None:
            return render_template('index.tmpl', brands=brands)
        else:
            print('GET model')
            models = getter.get_models(brand)
            print(models)
            models = json.dumps(models)
            print(models)
            return render_template('index.tmpl', brands=brands, models=models)

    return render_template('index.tmpl',brands=brands)


# @app.route("/data/get_models_for/<string:brand>", methods=["GET"])
# def get_models(brand):
#     getter = Data_Getter()
#     models = getter.get_models(brand)
#     models = json.dumps(models)
#     return jsonify(models)
#
#
# @app.route("/data/get_brands", methods=["GET"])
# def get_brands():
#     getter = Data_Getter()
#     brands = getter.get_brands()
#     result = json.dumps(brands)
#     return jsonify(result)

@app.route("/data/<string:args>", methods=["GET"])
def data_getter(args):
    getter = Data_Getter()
    getter_methods = {'get_brands': getter.get_brands, 'get_years_for': getter.get_years_for_model,
                      'get_engines_for': getter.get_engines, 'get_gearboxes_for': getter.get_gearboxes,
                      'get_models_for': getter.get_models}
    arguments = args.split('=')
    method = getter_methods[arguments[0]]
    if len(arguments) > 1:
        values_list = arguments[1].split('&')
    else:
        values_list = []
    result = method(*values_list)
    return jsonify(result)

# @app.route("/data/get_years_for/<string:brand>&<string:model>", methods=["GET"])
# def get_years(brand, model):
#     getter = Data_Getter()
#     years = getter.get_years_for_model(brand, model)
#     result = json.dumps(years)
#     return jsonify(result)
#
#
# @app.route("/data/get_engines_for/<string:brand>&<string:model>&<string:year>", methods=["GET"])
# def get_engines(brand, model, year):
#     getter = Data_Getter()
#     engines = getter.get_engines(brand, model, year)
#     result = json.dumps(engines)
#     return jsonify(result)
#
#
# @app.route("/data/get_gearboxes_for/<string:brand>&<string:model>&<string:year>&<string:engine>", methods=["GET"])
# def get_gearboxes(brand, model, year, engine):
#     getter = Data_Getter()
#     gearboxes = getter.get_gearboxes(brand, model, year, engine)
#     result = json.dumps(gearboxes)
#     return jsonify(result)


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

