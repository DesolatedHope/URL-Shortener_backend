from flask import Flask

app=Flask(__name__)
app.secret_key=b'c\xad\xfaX\xa6A\xce\xce\x01\x85\xc7\xb4\xb3V\xba.'

from app import controller
from app import views