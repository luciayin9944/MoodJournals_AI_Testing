## auth.py

from flask import Flask, request, jsonify, make_response
from flask_restful import Resource
from config import db
from models import *  
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required


class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')
        errors = []

        #validations
        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters")
        if not email or '@' not in email:
            errors.append("Invalid email")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters")
        if password != password_confirmation:
            errors.append("Passwords do not match")

        if errors:
            return jsonify({'errors': errors}), 400
        
        new_user = User(username=username)
        new_user.email = email
        new_user.password_hash = password
        
        try:
            db.session.add(new_user)
            db.session.commit()
            access_token = create_access_token(identity=str(new_user.id))
            response = make_response(jsonify({
                'token': access_token,
                'user': UserSchema().dump(new_user),
                'message': 'Signup successful!'
            }), 200)
            return response
        except IntegrityError:
            db.session.rollback()
            return {'errors': ['Username or Email already exists']}, 422
        


class WhoAmI(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            return UserSchema().dump(user), 200
        return {'errors': ['User not found']}, 404
    

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.authenticate(password):
            access_token = create_access_token(identity=str(user.id))
            response = make_response(jsonify(token=access_token, user=UserSchema().dump(user)), 200)
            return response
        return {'errors': ['Invalid email or password']}, 401