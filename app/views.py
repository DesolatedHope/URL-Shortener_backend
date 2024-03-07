from app import app
from app.models import db
from flask import redirect
from app.controller import getLongURL

domain="shorty.westeurope.cloudapp.azure.com/"

@app.route('/<shorturl>')
def redirectToWebsite(shorturl):
    longURL=getLongURL(shorturl)
    if not longURL=="URL Not Found":
        if not ('http://' in longURL or 'https://' in longURL):
            longURL='https://'+longURL
        return redirect(longURL,code=302)
    return "URL Not Found"

@app.route('/')
def index():
    return redirect('https://shortyaz.vercel.app/')