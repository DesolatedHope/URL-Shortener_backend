from app import app
from flask import Flask,jsonify,session
from flask_pymongo import PyMongo
import uuid
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import jwt_required,create_access_token,get_jwt_identity

app.config["MONGO_URI"]="mongodb://mongo:46D626gHedBg-6E5CdBfAhb4AGc-E2E5@roundhouse.proxy.rlwy.net:46054/shorty?authSource=admin"
db=PyMongo(app).db

class User:

    def create_token(self,email,password):
        user=db.users.find_one({"email":email})

        if not (user and pbkdf2_sha256.verify(password,user['password'])):
            return jsonify({"error":"Invalid Credentials"}),401
        
        access_token=create_access_token(identity=email)
        return jsonify(access_token=access_token),200

    def signup(self,user):

        user["_id"]=uuid.uuid4().hex
        user["password"]=pbkdf2_sha256.encrypt(user["password"])

        if db.users.find_one({"email":user["email"]}):
            return jsonify({"error":"Email address already in use"}),400

        if db.users.insert_one(user):
            access_token=create_access_token(identity=user['email'])
            return jsonify(access_token=access_token),200

        return jsonify({"error":"Something went wrong"}),400
    
    def signout(self):
        session.clear()
        return jsonify({"status":"Signout successful"})