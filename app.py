"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/

This file creates your application.
"""

import os
import os
import unirest
import json
import urllib2
from geopy.distance import vincenty
from flask import Flask, render_template, request, redirect, url_for,make_response,jsonify
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'this_should_be_configured')


###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')
app.route('/maps/')
def maps():
    """Render the website's about page."""
    return render_template('mapsexample.html')
app.route('/mapg/')
def maps():
    """Render the website's about page."""
    return render_template('mapg.html')
@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('mape.html')
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

@app.route('/api/')
def api():
    max_distance = float(request.args.get('max_distance'))
    latstart = float(request.args.get('latitude'))
    lngstart = float(request.args.get('longitude'))
    print(max_distance,latstart,lngstart)

    data = json.load(urllib2.urlopen('http://apps.who.int/gho/athena/api/GHO/WHOSIS_000001.json'))
    dataset = data['fact']
    besknownage = 0

    datacountries = unirest.get("https://restcountries-v1.p.mashape.com/all",
        headers={
            "X-Mashape-Key": "QFYbNVcpjJmsh0Qh8BjOmQlVu5dhp1bB0T8jsnZs1kzeBXgRsX",
            "Accept": "application/json"
        }
    )

    for fact in dataset:
        abc = process_fact(fact,data,float(max_distance),besknownage,float(latstart),float(lngstart),datacountries)
        if abc is not None:
            bestknowncountry = abc
            besknownage = abc[1]
    print (bestknowncountry[0],bestknowncountry[2],bestknowncountry[3])
    return jsonify({'state': bestknowncountry[0],'latitude': bestknowncountry[2],'longitude': bestknowncountry[3]})

###
# The functions below should be applicable to all Flask apps.
###

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
