from flask import Flask, render_template
import settings
import flickrapi
import random
app = Flask(__name__)

app.config.update(dict(
    BIRD_SELECTION=["northern cardinal", "egyptian vulture", "hooded warbler"],
    FLICKR_KEY=settings.FLICKR_KEY,
    FLICKR_SECRET=settings.FLICKR_SECRET,
    FLICKR_URL_FORMAT="https://farm{farm-id}.staticflickr.com/{server-id}/{id}_{secret}.jpg"
))

@app.route("/")
def hello():
    # pick a bird from app.config['BIRD_SELECTION'] at random
    bird = random.choice(app.config['BIRD_SELECTION'])
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

    # bring back a bird!
    return render_template('index.html', mystery_bird=birdurl)

if __name__ == "__main__":
    app.run()
