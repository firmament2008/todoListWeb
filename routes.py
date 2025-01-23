from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, validate
from extensions import db
from models import Todo

# 创建蓝图
todo_bp = Blueprint('todo', __name__)

# 验证模式
class TodoSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str()
    completed = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

# 待办事项路由
@todo_bp.route('', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    schema = TodoSchema(many=True)
    return jsonify(schema.dump(todos)), 200

@todo_bp.route('', methods=['POST'])
def create_todo():
    schema = TodoSchema()
    data = schema.load(request.json)
    
    todo = Todo(
        title=data['title'],
        description=data.get('description', '')
    )
    
    db.session.add(todo)
    db.session.commit()
    
    return jsonify(schema.dump(todo)), 201

@todo_bp.route('/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    schema = TodoSchema()
    data = schema.load(request.json)
    
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'message': '待办事项不存在'}), 404
    
    todo.title = data['title']
    todo.description = data.get('description', todo.description)
    
    # 处理完成状态变更
    new_completed = data.get('completed', todo.completed)
    if new_completed != todo.completed:
        if new_completed:
            todo.finish_time = datetime.utcnow()
        else:
            todo.finish_time = None
    
    # 如果是首次开始（从未完成状态变为已完成），设置开始时间
    if new_completed and not todo.start_time:
        todo.start_time = datetime.utcnow()
    
    todo.completed = new_completed
    db.session.commit()
    
    return jsonify(schema.dump(todo)), 200

@todo_bp.route('/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    
    if not todo:
        return jsonify({'message': '待办事项不存在'}), 404
    
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200