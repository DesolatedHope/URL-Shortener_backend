from app import app
from flask import request,jsonify
from app.models import db,User
from flask_cors import CORS, cross_origin
from flask_jwt_extended import jwt_required,get_jwt_identity
import datetime

CORS(app, resources={r"/api/*": {"origins": "*"}})

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
    shorturl=base10tobase62(counter)
    email=get_jwt_identity()
    db.variables.update_one({"_id":"counter"},{"$inc":{"counter":1}})
    db.variables.update_one({"_id":"counter"},{"$inc":{"websites":1}})
    db.variables.update_one({"_id":"counter"},{"$inc":{"active":1}})
    db.users.update_one({"email": email}, {"$inc": {"active": 1}})
    response={
        "_id":counter,
        "shortURL":shorturl,
        "longURL":longurl,
        "clicks":0,
        "user":email,
        "createdAt":datetime.datetime.now(),
        "isActive":True
    }
    db.websites.insert_one(response)
    response["shortURL"]=domain+shorturl
    db.users.update_one({"email": email}, {
        "$push": {
            "websites": response
        }
    })
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
        email=results['user']
        if results['isActive']==True:
            db.users.update_one({"email": email, "websites._id": results["_id"]}, {"$inc": {"websites.$.clicks": 1}})
            db.users.update_one({"email": email}, {"$inc": {"clicks": 1}})
            db.variables.update_one({"_id":"counter"},{"$inc":{"clicks":1}})
            db.websites.update_one({"shortURL":shorturl},{"$inc":{"clicks":1}})
        if results['isActive']==False or results['isActive']=='False':
            return "URL Not Found"
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

@app.route('/api/getTableData',methods=['GET'])
@cross_origin()
@jwt_required()
def getTableData():
    email=get_jwt_identity()
    result=db.users.find_one({"email":email})
    table=[]
    if result['websites']:
        table=result['websites']
        table=[{k:v for k,v in i.items() if k not in ['_id','user']} for i in table]
    return jsonify(dataTable=table)

@app.route('/api/alterStatus',methods=['POST'])
@cross_origin()
@jwt_required()
def inactivateURL():
    data=request.get_json()
    shortURL=data['shortURL']
    email=get_jwt_identity()
    shortURL=shortURL[-7:]
    result=db.websites.find_one({"shortURL":shortURL})
    if result['isActive']==True:
        db.variables.update_one({"_id":"counter"},{"$inc":{"active":-1}})
        db.users.update_one({"email": email}, {"$inc": {"active": -1}})
        db.websites.update_one({"shortURL":shortURL},{"$set":{"isActive":False}})
        db.users.update_one({"email": email, "websites._id": result["_id"]}, {"$set": {"websites.$.isActive": False}})
        return jsonify(status=False)
    else:
        db.variables.update_one({"_id":"counter"},{"$inc":{"active":1}})
        db.users.update_one({"email": email}, {"$inc": {"active": 1}})
        db.websites.update_one({"shortURL":shortURL},{"$set":{"isActive":True}})
        db.users.update_one({"email": email, "websites._id": result["_id"]}, {"$set": {"websites.$.isActive": True}})
        return jsonify(status=True)

    return jsonify({"message":"URL Inactivated"})

@app.route('/api/deleteURL',methods=['POST'])
@cross_origin()
@jwt_required()
def deleteURL():
    data=request.get_json()
    shortURL=data['shortURL']
    shortURL=shortURL[-7:]
    print(shortURL)
    email=get_jwt_identity()
    result=db.websites.find_one({"shortURL":shortURL})
    db.variables.update_one({"_id":"counter"},{"$inc":{"websites":-1}})
    if result['isActive']==True:
        db.variables.update_one({"_id":"counter"},{"$inc":{"active":-1}})
        db.users.update_one({"email": email}, {"$inc": {"active": -1}})
    db.users.update_one({"email": email}, {
        "$pull": {
            "websites": {
                "shortURL": shortURL
            }
        }
    })
    db.websites.delete_one({"shortURL":shortURL})
    return jsonify({"message":"URL Deleted"})

@app.route('/api/getPremium',methods=['POST'])
@cross_origin()
@jwt_required()
def getPremium():
    email=get_jwt_identity()
    db.users.update_one({"email": email}, {"$set": {"premium": True}})
    return jsonify(premium=True)

@app.route('/api/getAnalytics',methods=['GET'])
@cross_origin()
@jwt_required()
def getAnalytics():
    email=get_jwt_identity()
    result=db.users.find_one({"email":email})
    websites=len(result['websites'])
    clicks=result['clicks']
    active=result['active']
    data={
        "websites":websites,
        "clicks":clicks,
        "active":active
    }
    return jsonify(data),200

@app.route('/api/getStats',methods=['GET'])
@cross_origin()
def getStats():
    result=db.variables.find_one({"_id":"counter"})
    return jsonify(analytics=result)