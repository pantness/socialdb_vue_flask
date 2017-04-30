'''
api
'''

from pymongo import MongoClient
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from conf.config import MongoDBConfig

app = Flask(__name__)
client = MongoClient(MongoDBConfig.g_server_ip ,MongoDBConfig.g_server_port)
db = client[MongoDBConfig.g_db_name]

class Person(Resource):
    '''人员类'''
    def get(self, user=None, email=None, password=None, passwordHash=None):
        #data用于存储获取到的信息
        data = []

        if user and email:
            persons_info = db.person.find({"user": user, "email": email}, {"_id": 0})
        
        elif user:
            persons_info = db.person.find({"user": user}, {"_id": 0})
            
        elif email:
            persons_info = db.person.find({"email": email}, {"_id": 0})

        elif password:
            persons_info = db.person.find({"password": password}, {"_id": 0})
        
        elif passwordHash:
            persons_info = db.person.find({"password": password}, {"_id": 0})
            
        else:
            #此处限制只能查询10个
            persons_info = db.person.find({}, {"_id": 0, "update_time": 0}).limit(10)
 
        for person in persons_info:
            data.append(person)

        #判断有无数据返回 
        if data:
            return jsonify({"status": "ok", "data": data})
        else:
            return jsonify({"status": "not found", "data": ""})
            
    def post(self):
        '''
        以json格式进行提交文档
        '''
        data = request.get_json()
        if not data:
            return {"response": "ERROR DATA"}
        else:
            user = data.get('user')
            email = email.get('email')

            if user and email:
                if db.person.find_one({"user": user, "email": email}, {"_id": 0}):
                    return {"response": "{{} {} already exists.".format(user, email)}
                else:
                    db.person.insert(data)
            else:
                return redirect(url_for("person"))
    
    def put(self, user, email):
        '''
        根据user和email进行定位更新数据
        '''
        data = request.get_json()
        db.person.update({'user': user, 'email': email},{'$set': data})
        return redirect(url_for("person"))

    def delete(self, email):
        '''
        email作为唯一值, 对其进行删除
        '''
        db.person.remove({'email': email})
        return redirect(url_for("person"))


class Analysis(Resource):
    '''
    分析功能
    '''
    def get(self, type_analyze):
        '''
        type为分析类型，包括邮箱后缀、泄漏来源、泄漏时间
        type: [email, source, xtime]
        '''
        if type_analyze in ["source", "xtime"]:
            # type_args = request.args[type_analyze]

            # if type_args:
            #     persons = db.person.find({type_analyze:{"$regex":type_args}})
            
            # else:
            pipeline = [{"$group" : {"_id" : '$'+type_analyze, "sum" : {"$sum" : 1}}}]
            return jsonify({"status": "ok", "sum": db.person.find().count(), "data": list(db.person.aggregate(pipeline))})

        elif type_analyze is "email":
            pipeline 
        else:
            return jsonify({"status":"error", "response":"use api like /api/email/@qq.com or /api/email to get analysis data."})
        
        data = []
        for person in persons_info:
            data.append(person)

        if data:
            return jsonify({"status": "ok", "data": data, type_analyze:type_args})
        else:
            return jsonify({"status": "not found", "data": data, type_analyze:type_args})

#添加api资源
api = Api(app)
api.add_resource(Person, "/api/find")
api.add_resource(Person, "/api/find/user/<string:user>", endpoint="user")
api.add_resource(Person, "/api/find/email/<string:email>", endpoint="email")
api.add_resource(Person, "/api/find/pwd/<string:password>", endpoint="password")
api.add_resource(Analysis, "/api/analysis/<string:type_analyze>", endpoint="type_analyze")

if __name__ == '__main__':
    app.run(debug=True)