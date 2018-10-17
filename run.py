#!/usr/bin/env python

from flask import   Flask, render_template, send_from_directory, \
                    redirect, request, Response, stream_with_context, \
                    make_response, flash, url_for, send_from_directory, \
                    jsonify
import os, json, re
from dbapi.dbtools import Data_Getter

# api versioning
#from api.v1 import api as api_v1
#from api import common

app = Flask(__name__)


@app.route("/", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def index():
	with open('./static/index.html') as main_page:
	    title_sheet = main_page.read()
	return title_sheet


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


@app.route("/search", methods=["POST"])
def search():
    getter = Data_Getter()
    item = {'brand': '', 'model': '', 'year': '', 'kmage': '', 'engine': '', 'gearbox': ''}
    for key in request.form.keys():
	    if key in item.keys():
		    item[key] = request.form[key]
    points = getter.get_points(item)
    return f'FORM_KEYS: {request.form.keys()}\n'

#  description = ['avg_price', *[f'point{n}' for n in range(1, 6)]]
#  result = dict(zip(description, points))
#  return jsonify(result)

    
@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

