from flask_restful import Resource, reqparse
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import Column, String, create_engine, Integer
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt)
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
parser.add_argument('username', help = 'This field cannot be blank', required = True)
parser.add_argument('password', help = 'This field cannot be blank', required = True)

class UserRegistration(Resource):
    def post(self):
        data = parser.parse_args()
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
        data = parser.parse_args()
        engine = create_engine("sqlite:///" + DATABASE, echo=True)
        Base.metadata.create_all(engine)
        with Session(autoflush=False, bind=engine) as db:
            current_user = db.query(User).filter(User.username==data['username']).first()
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['username'])}
        
        if sha256.verify(data['password'], current_user.password):
            access_token = create_access_token(identity = data['username'])
            refresh_token = create_refresh_token(identity = data['username'])
            return {
                'message': 'Logged in as {}'.format(current_user.username),
                'access_token': access_token,
                'refresh_token': refresh_token
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
# Добавить обнуление прошлых токенов? Удаление из черного списка по дате добавления?
# Срок их действия большой, долгий поиск по базе каждый раз?

      
class SecretResource(Resource):
    @jwt_required()
    def get(self):
        return {
            'answer': 42
        }
      