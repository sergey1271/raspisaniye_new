from flask import Flask, render_template, request, session, redirect, flash, Response, make_response, jsonify
from flask_restful import Api, Resource, reqparse
from database_create import create_db  # создать базу данных
from flask_httpauth import HTTPBasicAuth  # аутентификация
from werkzeug.datastructures import FileStorage  # скачивание файлов на сервер
import os
from flask_jwt_extended import JWTManager, jwt_required
from flask_cors import CORS

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)
api = Api()
auth = HTTPBasicAuth()
app.config['UPLOAD_FOLDER'] = "C:\\Users\\mamin\\Desktop\\JSON_VERSION"
CORS(app)
import resources

@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return resources.RevokedTokenModel.is_jti_blocklisted(jti)

api.add_resource(resources.UserRegistration, '/registration')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.SecretResource, '/secret')
api.add_resource(resources.Send_classrooms_groups, '/send')
api.add_resource(resources.Test, '/test')

# Регистрация пользователя
# class Registration(Resource):
#     def post(self):
#         params = request.get_json(force=True)
#         if new(params["username"], params["password"]):
#             return make_response(jsonify(successfully=True), 200)
#             # 200
#         return make_response(jsonify(successfully=False), 409)
#         # 409 - Conflict/Конфликт
# api.add_resource(Registration, "/registration")

class Main(Resource):
    @jwt_required()
    def get(self):
        return make_response(jsonify(successfully=True), 200)
api.add_resource(Main, "/") 

# Вход в систему
# подумать над реализацией (cookie и т.п.)
# class Login(Resource):
#     @auth.verify_password
#     def post(self):
#         params = request.get_json(force=True)
#         if check(params["username"], params["password"]):
#             return True
#             # return make_response(jsonify(successfully=True))
#         return False
#         # return make_response(jsonify(successfully=False))
# api.add_resource(Login, "/login")

class GetInfo(Resource):
    def post(self):
        # Скачиваю файл:
        FileStorage(request.stream).save(os.path.join(app.config['UPLOAD_FOLDER'], "123.txt"))
        create_db("1234.db", "1234.txt")  # создаю БД
        return make_response(jsonify(successfully=True), 200)
api.add_resource(GetInfo, "/get_info")

api.init_app(app)

# @app.route('/get_info', methods=['GET', 'POST'])
# def get_info():
#     if request.method == "GET":
#         return render_template("get_info.html")
#     else:
#         response = Response()
#         response.data
#         db_name = request.form["teacher_name"]
#         dfile = request.form["dfile"]
#         create_db(db_name, dfile)
#         return render_template("get_info.html")
        
# !!!!! ВВОД ТИПОВ
if __name__ == '__main__':
    app.run(debug = True)
