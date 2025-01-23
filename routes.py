from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, validate, pre_load
from extensions import db
from models import Todo
from datetime import datetime

# 创建蓝图
todo_bp = Blueprint('todo', __name__)

# 验证模式
class TodoSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(allow_none=True)
    completed = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    start_time = fields.DateTime(allow_none=True)
    finish_time = fields.DateTime(allow_none=True)

    @staticmethod
    def _deserialize_datetime_field(value):
        if value == "":
            return None
        return value

    @pre_load
    def process_datetime_fields(self, data, **kwargs):
        if 'start_time' in data:
            data['start_time'] = self._deserialize_datetime_field(data['start_time'])
        if 'finish_time' in data:
            data['finish_time'] = self._deserialize_datetime_field(data['finish_time'])
        return data

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
            todo.start_time = datetime.now()
        
        # 如果标记为已完成且没有设置完成时间，则设置为当前时间
        if todo.completed and not todo.finish_time:
            todo.finish_time = datetime.now()
        
        db.session.add(todo)
        db.session.commit()
        
        return jsonify(schema.dump(todo)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'创建待办事项失败: {str(e)}'}), 400

@todo_bp.route('/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    try:
        schema = TodoSchema()
        data = schema.load(request.json)
        
        todo = Todo.query.get(todo_id)
        if not todo:
            return jsonify({'message': '待办事项不存在'}), 404
        
        todo.title = data['title']
        todo.description = data.get('description')
        
        # 更新时间字段，允许设置为None
        if 'start_time' in data:
            todo.start_time = data['start_time']
        if 'finish_time' in data:
            todo.finish_time = data['finish_time']
        
        # 处理完成状态变更
        new_completed = data.get('completed', todo.completed)
        if new_completed != todo.completed:
            if new_completed:
                # 如果是首次完成且没有设置完成时间，则设置为当前时间
                if not todo.finish_time:
                    todo.finish_time = datetime.now()
                # 如果是首次完成且没有设置开始时间，则设置为当前时间
                if not todo.start_time:
                    todo.start_time = datetime.now()
            else:
                # 如果取消完成，则清除完成时间
                todo.finish_time = None
        
        todo.completed = new_completed
        db.session.commit()
        
        return jsonify(schema.dump(todo)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'更新待办事项失败: {str(e)}'}), 400

@todo_bp.route('/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.filter(Todo.id == todo_id, Todo.deleted_at == None).first()
    
    if not todo:
        return jsonify({'message': '待办事项不存在'}), 404
    
    todo.deleted_at = datetime.now()
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

@todo_bp.route('/deleted/permanent/<int:todo_id>', methods=['DELETE'])
def permanent_delete_todo(todo_id):
    todo = Todo.query.filter(Todo.id == todo_id, Todo.deleted_at != None).first()
    
    if not todo:
        return jsonify({'message': '待办事项不存在或未被删除'}), 404
    
    try:
        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message': '永久删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'永久删除失败: {str(e)}'}), 400

@todo_bp.route('/deleted/permanent/batch', methods=['DELETE'])
def permanent_delete_todos_batch():
    try:
        todo_ids = request.json.get('ids', [])
        if not todo_ids:
            return jsonify({'message': '未选择要删除的待办事项'}), 400
            
        todos = Todo.query.filter(Todo.id.in_(todo_ids), Todo.deleted_at != None).all()
        if not todos:
            return jsonify({'message': '未找到要删除的待办事项'}), 404
            
        for todo in todos:
            db.session.delete(todo)
        
        db.session.commit()
        return jsonify({'message': f'成功永久删除 {len(todos)} 个待办事项'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'批量永久删除失败: {str(e)}'}), 400

@todo_bp.route('/deleted/permanent/all', methods=['DELETE'])
def permanent_delete_all_todos():
    try:
        todos = Todo.query.filter(Todo.deleted_at != None).all()
        if not todos:
            return jsonify({'message': '垃圾桶为空'}), 404
            
        for todo in todos:
            db.session.delete(todo)
            
        db.session.commit()
        return jsonify({'message': f'成功清空垃圾桶，删除了 {len(todos)} 个待办事项'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'清空垃圾桶失败: {str(e)}'}), 400