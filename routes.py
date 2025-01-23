from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, validate
from extensions import db
from models import User, Todo

# 创建蓝图
auth_bp = Blueprint('auth', __name__)
todo_bp = Blueprint('todo', __name__)

# 验证模式
class UserSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6))

class TodoSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    completed = fields.Bool()

# 用户认证路由
@auth_bp.route('/register', methods=['POST'])
def register():
    schema = UserSchema()
    data = schema.load(request.json)
    
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': '用户名已存在'}), 400
    
    user = User(username=data['username'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': '注册成功'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    schema = UserSchema()
    data = schema.load(request.json)
    
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'message': '用户名或密码错误'}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify({'access_token': access_token}), 200

# 待办事项路由
@todo_bp.route('', methods=['GET'])
@jwt_required()
def get_todos():
    user_id = get_jwt_identity()
    todos = Todo.query.filter_by(user_id=user_id).all()
    schema = TodoSchema(many=True)
    return jsonify(schema.dump(todos)), 200

@todo_bp.route('', methods=['POST'])
@jwt_required()
def create_todo():
    schema = TodoSchema()
    data = schema.load(request.json)
    user_id = get_jwt_identity()
    
    todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        user_id=user_id
    )
    
    db.session.add(todo)
    db.session.commit()
    
    return jsonify(schema.dump(todo)), 201

@todo_bp.route('/<int:todo_id>', methods=['PUT'])
@jwt_required()
def update_todo(todo_id):
    schema = TodoSchema()
    data = schema.load(request.json)
    user_id = get_jwt_identity()
    
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    if not todo:
        return jsonify({'message': '待办事项不存在'}), 404
    
    todo.title = data['title']
    todo.description = data.get('description', todo.description)
    todo.completed = data.get('completed', todo.completed)
    
    db.session.commit()
    
    return jsonify(schema.dump(todo)), 200

@todo_bp.route('/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    user_id = get_jwt_identity()
    todo = Todo.query.filter_by(id=todo_id, user_id=user_id).first()
    
    if not todo:
        return jsonify({'message': '待办事项不存在'}), 404
    
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200