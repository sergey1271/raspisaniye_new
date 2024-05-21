from flask_restful import Resource, reqparse
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import Column, String, create_engine, Integer
from passlib.hash import pbkdf2_sha256 as sha256
from flask_cors import cross_origin
from flask import request, jsonify, Response, url_for, send_file, send_from_directory
import simplejson as json
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
from database_create import create_db, add_times
from export_timetable import create_file_to_user, read_file
from werkzeug import datastructures
import os
import datetime
from timetable_create import timetable_generation
DATABASE = 'REGISTRATION.db'
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True)
    password = Column(String)

class RevokedTokenModel(Base):
    __tablename__ = 'revoked_tokens'
    id = Column(Integer, primary_key = True)
    jti = Column(String)
    
    def add(self):
        engine = create_engine("sqlite:///" + DATABASE, echo=True)
        Base.metadata.create_all(engine)
        with Session(autoflush=False, bind=engine) as db:
                    db.add(self)
                    db.commit()
    
    @classmethod
    def is_jti_blocklisted(cls, jti):
        engine = create_engine("sqlite:///" + DATABASE, echo=True)
        Base.metadata.create_all(engine)
        with Session(autoflush=False, bind=engine) as db:
            query = db.query(cls).filter_by(jti = jti).first()
        return bool(query)

parser = reqparse.RequestParser()
parser.add_argument('username', required = True)
parser.add_argument('password', required = True)

class UserRegistration(Resource):
    def post(self):
        #data = parser.parse_args()
        data = request.json
        try:
            engine = create_engine("sqlite:///" + DATABASE, echo=True)
            Base.metadata.create_all(engine)
            username = data['username']
            p_hash = sha256.hash(data["password"])
            with Session(autoflush=False, bind=engine) as db:
                    usr = User(username=username, password=p_hash)
                    db.add(usr)
                    db.commit()
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'User {} was created'.format(data['username']),
                'access_token': access_token,
                'refresh_token': refresh_token
                }
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        # data = parser.parse_args()
        data = request.json
        engine = create_engine("sqlite:///" + DATABASE, echo=True)
        Base.metadata.create_all(engine)
        with Session(autoflush=False, bind=engine) as db:
            current_user = db.query(User).filter(User.username==data['username']).first()
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if sha256.verify(data['password'], current_user.password):
            access_token = create_access_token(identity = data['username'], expires_delta=datetime.timedelta(0, 60))
            refresh_token = create_refresh_token(identity = data['username'], expires_delta=datetime.timedelta(0, 900))
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'successfully': 'true'
                }
        else:
            return {'message': 'Wrong credentials'}

class UserLogoutAccess(Resource):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
      
      
class UserLogoutRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        jti = get_jwt()['jti']
        try:
            revoked_token = RevokedTokenModel(jti = jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
      
      
class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity = current_user, fresh=False)
        refresh_token = create_refresh_token(identity = current_user)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
                }
# Удаление из черного списка по дате добавления?
# Срок их действия большой, долгий поиск по базе каждый раз?

      
class SecretResource(Resource):
    @jwt_required()
    def get(self):
        return {
            'answer': 42
        }

class Test(Resource):
    def post(self):
        print(123)
        # data = parser.parse_args()
        data = request.json
        print(data["username"])
        return None

class Send_classrooms_groups(Resource):
    @jwt_required()
    def post(self):
        try:
            data = request.json
            clrms = data["classrooms"]
            print(clrms)
            create_db(f'{data["username"]}.db', data["groups"], data["classrooms"], data["subjects"], data['teachers'])
            print(12345)
            return {'successfully': 'true'}
        except:
            return {'successfully': 'false'}

class Get_excel(Resource):
    def post(self):
        print("-----------------------------------------")
        # data = parser.parse_args()
        try:
            data = request.json
            print(data["username"])
            create_file_to_user(f'{data["username"]}.xlsx', f'{data["username"]}.db')
            return send_file('data/lyceum1524.xlsx', download_name="12344.xlsx", as_attachment=True)
        except:
            return jsonify(successfully=False)
    def get(self):
        print("Был GET запрос")
        return send_file('data/lyceum1524.xlsx', download_name="12344.xlsx")

class ReadFile(Resource):
    def post(self):
        # data = parser.parse_args()
        try:
            file = request.files['file']
            data = request.form
            print(data["username"])
            print(file)
            file.save(os.path.join("uploads", f'{data["username"]}.xlsx'))
            read_file(f'uploads/{data["username"]}.xlsx', f'{data["username"]}.db')
            return {'successfully': 'true'}
        except:
            return {'successfully': 'false'}

class Generate(Resource):
    def post(self):
        # data = parser.parse_args()
        try:
            data = request.json
            print(data["username"])
            print(12345)
            timetable_generation(data["username"])
            return {'successfully': 'true'}
        except:
            return {'successfully': 'false'}
        

class Download(Resource):
    def post(self):
        # data = parser.parse_args()
        try:
            data = request.json
            print(data["username"])
            return send_file('data/lyceum1524.xlsx', download_name="12344.xlsx", as_attachment=True)
        except:
            return send_file(f'data/{data["username"]}_rasp.xlsx', download_name="12344.xlsx")

class SendTimes(Resource):
    def post(self):
        # data = parser.parse_args()
        try:
            # data = parser.parse_args()
            
            data = request.json
            add_times(f'{data["username"]}.db', data["saturday"], data['starts'], data['finishes'])
            print(12345)
            return {'successfully': 'true'}
        except:
            return {'successfully': 'false'}