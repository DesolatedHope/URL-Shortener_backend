from flask import Flask
from flask_cors import CORS

app=Flask(__name__)
app.secret_key=b'c\xad\xfaX\xa6A\xce\xce\x01\x85\xc7\xb4\xb3V\xba.'

CORS(app, origins=['http://localhost:3000'], methods=['GET', 'POST'], allow_headers=['Content-Type'])

from app import controller
from app import views