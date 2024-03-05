from flask import Flask
from flask_jwt_extended import JWTManager

app=Flask(__name__)
app.secret_key=b'c\xad\xfaX\xa6A\xce\xce\x01\x85\xc7\xb4\xb3V\xba.'
app.config["JWT_SECRET_KEY"]=b'\\\xe0\x88\xe7/\x01\x95J*\xde;\xdc'
jwt=JWTManager(app)

from app import controller
from app import views