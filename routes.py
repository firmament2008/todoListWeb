from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, validate
from extensions import db
from models import Todo
from datetime import datetime

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
    start_time = fields.DateTime(allow_none=True, format='%Y-%m-%d %H:%M:%S')
    finish_time = fields.DateTime(allow_none=True, format='%Y-%m-%d %H:%M:%S')

# 待办事项路由
@todo_bp.route('', methods=['GET'])
def get_todos():
    todos = Todo.query.filter(Todo.deleted_at == None).all()
    schema = TodoSchema(many=True)
    return jsonify(schema.dump(todos)), 200

@todo_bp.route('', methods=['POST'])
def create_todo():
    try:
        schema = TodoSchema()
        data = schema.load(request.json)
        
        # 创建待办事项，添加默认值和时间处理
        todo = Todo(
            title=data['title'],
            description=data.get('description', ''),
            start_time=data.get('start_time'),
            finish_time=data.get('finish_time'),
            completed=data.get('completed', False)
        )
        
        # 如果标记为已完成且没有设置开始时间，则设置为当前时间
        if todo.completed and not todo.start_time:
            todo.start_time = datetime.utcnow()
        
        # 如果标记为已完成且没有设置完成时间，则设置为当前时间
        if todo.completed and not todo.finish_time:
            todo.finish_time = datetime.utcnow()
        
        db.session.add(todo)
        db.session.commit()
        
        return jsonify(schema.dump(todo)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建待办事项失败: {str(e)}'}), 400

@todo_bp.route('/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    schema = TodoSchema()
    print("请求载荷:", request.json)  # 打印请求载荷
    data = schema.load(request.json)
    
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'message': '待办事项不存在'}), 404
    
    todo.title = data['title']
    todo.description = data.get('description', todo.description)
    
    # 更新时间字段
    todo.start_time = data.get('start_time', todo.start_time)
    todo.finish_time = data.get('finish_time', todo.finish_time)
    print("更新后的时间字段:", {"start_time": todo.start_time, "finish_time": todo.finish_time})  # 打印更新后的时间字段
    
    # 处理完成状态变更
    new_completed = data.get('completed', todo.completed)
    if new_completed != todo.completed:
        if new_completed:
            todo.finish_time = datetime.utcnow()
        else:
            todo.finish_time = None
    
    # 如果是首次开始且没有设置start_time，则自动设置为当前时间
    if new_completed and not todo.start_time:
        todo.start_time = datetime.utcnow()
    
    todo.completed = new_completed
    db.session.commit()
    
    return jsonify(schema.dump(todo)), 200

@todo_bp.route('/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.filter(Todo.id == todo_id, Todo.deleted_at == None).first()
    
    if not todo:
        return jsonify({'message': '待办事项不存在'}), 404
    
    todo.deleted_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': '删除成功'}), 200

@todo_bp.route('/deleted', methods=['GET'])
def get_deleted_todos():
    todos = Todo.query.filter(Todo.deleted_at != None).all()
    schema = TodoSchema(many=True)
    return jsonify(schema.dump(todos)), 200

@todo_bp.route('/<int:todo_id>/restore', methods=['PUT'])
def restore_todo(todo_id):
    todo = Todo.query.filter(Todo.id == todo_id, Todo.deleted_at != None).first()
    
    if not todo:
        return jsonify({'message': '待办事项不存在或未被删除'}), 404
    
    todo.deleted_at = None
    db.session.commit()
    
    return jsonify({'message': '恢复成功'}), 200