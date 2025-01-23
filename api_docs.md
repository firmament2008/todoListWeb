# TodoList API 接口文档

## 基础信息
- 基础URL: `http://localhost:5000`
- 响应格式: JSON
- 时间格式: ISO 8601 (例如: "2024-01-01T12:00:00")

## 待办事项管理

### 1. 获取所有待办事项

```
GET /todo
```

**响应示例:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "完成项目",
      "description": "完成TodoList项目的开发",
      "completed": false,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00",
      "start_time": "2024-01-01T10:00:00",
      "finish_time": null
    }
  ]
}
```

### 2. 创建待办事项

```
POST /todo
```

**请求参数:**
```json
{
  "title": "string(必填，1-200字符)",
  "description": "string(可选)",
  "completed": "boolean(可选，默认false)",
  "start_time": "datetime(可选)",
  "finish_time": "datetime(可选)"
}
```

**响应示例:**
```json
{
  "id": 1,
  "title": "新待办事项",
  "description": "描述信息",
  "completed": false,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00",
  "start_time": null,
  "finish_time": null
}
```

### 3. 更新待办事项

```
PUT /todo/{todo_id}
```

**请求参数:**
```json
{
  "title": "string(必填，1-200字符)",
  "description": "string(可选)",
  "completed": "boolean(可选)",
  "start_time": "datetime(可选)",
  "finish_time": "datetime(可选)"
}
```

**响应示例:**
```json
{
  "id": 1,
  "title": "更新后的标题",
  "description": "更新后的描述",
  "completed": true,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T11:00:00",
  "start_time": "2024-01-01T10:00:00",
  "finish_time": "2024-01-01T11:00:00"
}
```

### 4. 删除待办事项（软删除）

```
DELETE /todo/{todo_id}
```

**响应示例:**
```json
{
  "message": "删除成功"
}
```

## 已删除待办事项管理

### 1. 获取已删除的待办事项

```
GET /todo/deleted
```

**响应示例:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "已删除的待办事项",
      "description": "描述信息",
      "completed": false,
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00",
      "start_time": null,
      "finish_time": null
    }
  ]
}
```

### 2. 恢复已删除的待办事项

```
PUT /todo/{todo_id}/restore
```

**响应示例:**
```json
{
  "message": "恢复成功"
}
```

### 3. 永久删除单个待办事项

```
DELETE /todo/deleted/permanent/{todo_id}
```

**响应示例:**
```json
{
  "message": "永久删除成功"
}
```

### 4. 批量永久删除待办事项

```
DELETE /todo/deleted/permanent/batch
```

**请求参数:**
```json
{
  "ids": [1, 2, 3]
}
```

**响应示例:**
```json
{
  "message": "成功永久删除 3 个待办事项"
}
```

### 5. 清空回收站（永久删除所有已删除的待办事项）

```
DELETE /todo/deleted/permanent/all
```

**响应示例:**
```json
{
  "message": "成功清空垃圾桶，删除了 5 个待办事项"
}
```

## 错误响应

当请求出现错误时，API会返回相应的错误信息：

```json
{
  "message": "错误信息描述"
}
```

常见错误状态码：
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 注意事项

1. 创建和更新待办事项时，如果将completed设置为true：
   - 如果未设置start_time，将自动设置为当前时间
   - 如果未设置finish_time，将自动设置为当前时间

2. 更新待办事项时，如果将completed从true改为false：
   - finish_time将被清除（设置为null）

3. 所有的时间字段都可以通过传入空字符串("")来设置为null