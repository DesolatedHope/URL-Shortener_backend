from app import app
from flask import request,jsonify
from app.models import db,User
from flask_cors import CORS, cross_origin
from flask_jwt_extended import jwt_required,get_jwt_identity

CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

elements="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
domain="shorty.westeurope.cloudapp.azure.com/"

def base10tobase62(num):
    ret=''
    while num:
        ret+=elements[num%62]
        num//=62
    while len(ret)!=7:
        ret+='0'
    return ret

@app.route('/api/getShortURL',methods=["GET","POST"])
@cross_origin()
@jwt_required()
def shortenURL():
    data=request.get_json()
    longurl=data['longURL']
    results=db.variables.find_one({"_id":"counter"})
    counter=results["counter"]
    print(counter)
    shorturl=base10tobase62(counter)
    email=get_jwt_identity()
    db.variables.update_one({"_id":"counter"},{"$inc":{"counter":1}})
    response={
        "shortURL":shorturl,
        "longURL":longurl,
        "_id":counter
    }
    db.websites.insert_one(response)
    response["shortURL"]=domain+shorturl
    return response

@app.route('/api/getLongURL',methods=["GET","POST"])
@cross_origin()
def redirect():
    data=request.get_json()
    shorturl=data['shortURL']
    results=db.websites.find_one({"shortURL":shorturl})
    if results:
        longURL=results['longURL']
        return jsonify(longURL),200
    return jsonify({"error":"URL Not Found"}),404

def getLongURL(shorturl):
    results=db.websites.find_one({"shortURL":shorturl})
    if results:
        longURL=results['longURL']
        return longURL
    return "URL Not Found"

@app.route('/api/createToken',methods=['POST'])
@cross_origin()
def create_token():
    email=request.get_json()['email']
    password=request.get_json()['password']
    return User().create_token(email,password)

@app.route('/api/signup',methods=['POST'])
@cross_origin()
def signup():
    user=request.get_json()
    return User().signup(user)