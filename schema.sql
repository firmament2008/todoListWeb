CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    start_time DATETIME,
    finish_time DATETIME
);

-- 创建索引以优化查询性能
CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(completed);
CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at);

-- 添加软删除字段
ALTER TABLE todos ADD COLUMN deleted_at DATETIME;

-- 为软删除字段创建索引以优化查询性能
CREATE INDEX IF NOT EXISTS idx_todos_deleted_at ON todos(deleted_at);
