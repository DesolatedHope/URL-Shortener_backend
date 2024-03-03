from app import app
from app.models import db
import requests
import json
from flask import redirect

apiurl='http://127.0.0.1:5000/api/getLongURL'

@app.route('/<shorturl>')
def redirectToWebsite(shorturl):
    shorturl='shorty.az/'+shorturl
    data={
        "shortURL":shorturl
    }
    response=requests.post(apiurl,json=data)
    if response.status_code==200:
        longURL=response.json()
        if not ('http://' in longURL or 'https://' in longURL):
            longURL='https://'+longURL
        return redirect(longURL,code=302)
    else:
        return "URL Not Found",404
    return "Hello World"
