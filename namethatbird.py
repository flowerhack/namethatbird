from flask import Flask, render_template, request, session
import settings
from pygeocoder import Geocoder
#import flickrapi

import random
import sqlite3
from flask import g
import os

import sys
sys.path.insert(0, "/Users/juliahansbrough/Desktop/Programming/flickrapi/flickrapi")
import flickrapi

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'birds.db'),
    BIRD_SELECTION=["northern cardinal", "egyptian vulture", "hooded warbler"],
    FLICKR_KEY=settings.FLICKR_KEY,
    FLICKR_SECRET=settings.FLICKR_SECRET,
    FLICKR_URL_FORMAT="https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg"
))

app.secret_key = settings.SESSION_SECRET

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    return rv

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connct_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/", methods=['GET','POST'])
def hello():
    if request.method == 'POST':
        if request.form.get('diff'):
            session['difficulty'] = int(request.form.get('diff'))
    #    if request.form.get('guessedname'):
    #        if request.form.get('guessedname') == prev:
    #            prev_result = "Correct!"
    #        else:
    #            prev_result = "lolfail"
    if 'difficulty' not in session:
        # default is easy
        session['difficulty'] = 1
        

    data = connect_db()
    # code=1 is easy mode
    bird = random.choice([i for i in data.execute(
        'select name from birds where code<=' + str(session['difficulty']) + ';'
    )])[0]
    # query the flickr api
    flickr = flickrapi.FlickrAPI(app.config['FLICKR_KEY'], app.config['FLICKR_SECRET'])
    photogen = flickr.walk(text=bird)
    bird_photo = photogen.next()
    birddict = {}
    for item in bird_photo.items():
        birddict[item[0]] = item[1]

    birdurl = app.config['FLICKR_URL_FORMAT'].replace(
        '{farm-id}', birddict['farm']
    ).replace(
        '{server-id}', birddict['server']
    ).replace(
        '{id}', birddict['id']
    ).replace(
        '{secret}', birddict['secret']
    )

    resulting_location = ""
    try:
        geoloc = flickr.photos.geo.getLocation(photo_id=birddict['id'])
        geodata = geoloc.getchildren()[0].getchildren()[0].items()
        resulting_location = str(Geocoder.reverse_geocode(float(geodata[4][1]), float(geodata[2][1])))
    except:
        pass

    date = ""
    try:
        photoinfo = flickr.photos.getInfo(photo_id=birddict['id'])
        date = "Taken " + photoinfo.getchildren()[0].getchildren()[4].items()[0][1]
    except:
        pass

    return render_template('index.html', mystery_bird=birdurl, diff=session['difficulty'], location=resulting_location, date=date)

if __name__ == "__main__":
    app.run()
