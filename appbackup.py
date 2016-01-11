"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""
#!/usr/bin/env python3

#import connexion
import os
#import werkzeug.urls
from geopy.distance import vincenty
import unirest
import json
import urllib2
from flask import Flask, render_template, request, redirect, url_for
from flask import make_response,jsonify
#from werkzeug.exceptions import default_exceptions, HTTPException
from flask import make_response, abort as flask_abort, request
#from flask.exceptions import JSONHTTPException
from flask.ext.cors import CORS, cross_origin
from flask import request

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


###
# Routing for your application.
###

@app.route('/')
@cross_origin()
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
@cross_origin()
def about():
    """Render the website's about page."""
    return render_template('about.html')


def process_fact(fact,data,maxdistance,bestknownlife,latstart,lngstart,datacountries):
    #@50.0752962,14.419395,16.5z?hl=en
    # latstart = 50.0752962
    # lngstart = 14.419395

    age = fact["value"]["numeric"]
    countryname = "none"
    countrycode = "none"
    info = fact["Dim"]
    for category in info:
        if 'YEAR' == category["category"]:
            if category["code"] != '2013':
                return
        if 'SEX' == category["category"]:
            if category["code"] != 'FMLE':
                return
        #if 'REGION' == category["category"]:
        #   if category["code"] != 'EUR':
        #       return
    for category in info:
        if 'COUNTRY' == category["category"]:
            countrycode = category["code"]
    for country in data['dimension'][5]['code']:
        if country['label'] == countrycode:
            countryname = country['display']
            break
    if countryname == "none":
        return
    for con in datacountries.body:
        if con["alpha3Code"] == countrycode:
            lat = con["latlng"][0]
            lng = con["latlng"][1]
            #print(countryname)

    start = (latstart, lngstart)
    end = (lat, lng)
    distance = vincenty(start, end).kilometers
    if distance > maxdistance:
        return
    if age > bestknownlife:
        #print(age, countryname)
        return (countryname,age,lat,lng)
app.route('/api2/',methods=['GET'])
@cross_origin()
def api2():
    return render_template('about.html')
app.route('/api2/',methods=['GET'])
@cross_origin()
def api():
    #if not request.json or not 'max_distance' in request.json:
    #    flask_abort(400)
    #max_distance = request.json['max_distance']
    #latstart = request.json['latitude']
    #lngstart = request.json['longtitude']
    max_distance = request.args.get('max_distance')
    latstart = request.args.get('latstart')
    lngstart = request.args.get('longtitude')

    data = json.load(urllib2.urlopen('http://apps.who.int/gho/athena/api/GHO/WHOSIS_000001.json'))
    dataset = data['fact']
    besknownage = 0

    datacountries = unirest.get("https://restcountries-v1.p.mashape.com/all",
        headers={
            "X-Mashape-Key": "QFYbNVcpjJmsh0Qh8BjOmQlVu5dhp1bB0T8jsnZs1kzeBXgRsX",
            "Accept": "application/json"
        }
    )

    #http://maps.googleapis.com/maps/api/geocode/json?address=Hungary&sensor=false
    for fact in dataset:
        abc = process_fact(fact,data,float(max_distance),besknownage,float(latstart),float(lngstart),datacountries)
        if abc is not None:
            bestknowncountry = abc
            besknownage = abc[1]
   # print(bestknowncountry)
   #  origin = request.headers['Origin']
   #  response = make_response({'state': bestknowncountry[0],'latitude': bestknowncountry[2],'longtitude': bestknowncountry[3]})
   #  response.headers['Access-Control-Allow-Origin'] = origin
   #  return response

    return jsonify({'state': bestknowncountry[0],'latitude': bestknowncountry[2],'longtitude': bestknowncountry[3]})


    #return redirect("http://apps.who.int/gho/athena/api/GHO/WHOSIS_000001.json")

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)

def any_response(data):
  #ALLOWED = ['http://localhost:8888']
  response = make_response(data)
  origin = request.headers['Origin']
  #if origin in ALLOWED:
  response.headers['Access-Control-Allow-Origin'] = origin
  return response
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response

@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'code':'','400': 'Bad request, should be the Maximal distance,'
                                                   'Latitude component of location,Longitude component of location all as doubles'}), 400)
@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)