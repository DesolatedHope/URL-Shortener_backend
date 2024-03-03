from app import app
from flask import request,jsonify
from app.models import db,User

elements="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def base10tobase62(num):
    ret=''
    while num:
        ret+=elements[num%62]
        num//=62
    while len(ret)!=7:
        ret+='0'
    return ret

@app.route('/api/getShortURL',methods=["GET","POST"])
def shortenURL():
    data=request.get_json()
    longurl=data['longURL']
    results=db.variables.find_one({"_id":"counter"})
    counter=results["counter"]
    print(counter)
    shorturl=base10tobase62(counter)
    shorturl="shorty.az/"+shorturl
    db.variables.update_one({"_id":"counter"},{"$inc":{"counter":1}})
    response={
        "shortURL":shorturl,
        "longURL":longurl,
        "_id":counter
    }
    db.websites.insert_one(response)
    return response

@app.route('/api/getLongURL',methods=["GET","POST"])
def redirect():
    data=request.get_json()
    shorturl=data['shortURL']
    results=db.websites.find_one({"shortURL":shorturl})
    if results:
        longURL=results['longURL']
        return jsonify(longURL),200
    return jsonify({"error":"URL Not Found"}),404

@app.route('/api/user/signup',methods=['POST'])
def signup():
    user=request.get_json()
    return User().signup(user)

@app.route('/api/user/signout',methods=['POST'])
def signout():
    return User().signout()

@app.route('/api/user/login',methods=['POST'])
def login():
    user=request.get_json()
    return User().login(user)