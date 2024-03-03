from app import app
from app.models import db
from flask import redirect
from app.controller import getLongURL

@app.route('/<shorturl>')
def redirectToWebsite(shorturl):
    shorturl='shorty.az/'+shorturl
    longURL=getLongURL(shorturl)
    if not longURL=="URL Not Found":
        if not ('http://' in longURL or 'https://' in longURL):
            longURL='https://'+longURL
        return redirect(longURL,code=302)
    return "URL Not Found"

@app.route('/')
def index():
    return "Welcome to Shorty.az"