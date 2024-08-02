from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from typing import Dict, Any
import validators
from src.constants.http_status_codes import(HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_200_OK)
from src.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flasgger import swag_from

auth = Blueprint("auth",__name__,url_prefix="/api/v1/auth")


@auth.post('/register')
@swag_from('docs/auth/register.yaml')
def register()-> str:
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']
    if len(password) < 6:
        return jsonify({"error":"password is too short"}),HTTP_400_BAD_REQUEST,
    
    
    if len(username) < 3:
        return jsonify({"error":"user is too short"}),HTTP_400_BAD_REQUEST,
    
    if not username.isalnum() or " " in username:
        return jsonify({"error":"Username should be alphanumeric, also no space allowed"}), HTTP_400_BAD_REQUEST 
    
    if not validators.email(email):
        return jsonify({"error":"Email is not valid"}),HTTP_400_BAD_REQUEST
    
    if  User.query.filter_by(email=email).first() is not None:
         return jsonify({"error":"Email is already taken!"}),HTTP_409_CONFLICT 
    
    if  User.query.filter_by(username=username).first() is not None:
         return jsonify({"error":"Email is already taken!"}),HTTP_409_CONFLICT 
     
    
    pwd_hash = generate_password_hash(password)
    
    user = User(username=username,password=pwd_hash,email=email)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': "User created",
        'user': {
            'username': username, "email": email
        }

    }), HTTP_201_CREATED

@auth.post("/login")
@swag_from('docs/auth/login.yaml')

def login()-> Any:
    email = request.json.get('email','')
    password = request.json.get('password','')
    
    user = User.query.filter_by(email=email).first()
    
    if user:
        is_pass_correct = check_password_hash(user.password, password)
        
        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)
            
            return jsonify({
                'refresh': refresh,
                'access': access,
                'user': {
                    'username': user.username,
                    'email': user.email
                }
            }), HTTP_200_OK
    
    return jsonify({'error':'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'username': user.username,
        'email':user.email
    }), HTTP_200_OK

@auth.post("/token/refresh")
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    
    return jsonify({
        'access': access
    }), HTTP_200_OK