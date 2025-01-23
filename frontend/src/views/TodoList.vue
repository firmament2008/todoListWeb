<template>
  <div class="todo-container">
    <el-card class="todo-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2 class="title">待办事项</h2>
            <el-input
              v-model="searchQuery"
              placeholder="搜索待办事项"
              prefix-icon="Search"
              clearable
              class="search-input"
              @input="handleSearch"
            />
            <el-select v-model="statusFilter" placeholder="状态过滤" class="status-filter">
              <el-option label="全部" value="all" />
              <el-option label="未完成" value="incomplete" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </div>
          <div class="header-right">
            <el-button type="info" @click="showDeletedTodos = true">
              <el-icon><Delete /></el-icon>
              垃圾桶
            </el-button>
            <el-button type="primary" @click="dialogVisible = true">添加待办</el-button>
          </div>
        </div>
      </template>

      <el-table v-loading="loading" :data="sortedTodos" style="width: 100%" @sort-change="handleSortChange">
        <el-table-column prop="title" label="标题" min-width="120" sortable="custom" :sort-orders="['ascending', 'descending']" :sort-by="'title'"></el-table-column>
        <el-table-column prop="description" label="描述" min-width="180"></el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="160" sortable="custom" :sort-orders="['ascending', 'descending']" :sort-by="'start_time'">
          <template #default="{ row }">
            {{ row.start_time ? new Date(row.start_time).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="finish_time" label="完成时间" width="160" sortable="custom" :sort-orders="['ascending', 'descending']" :sort-by="'finish_time'">
          <template #default="{ row }">
            {{ row.finish_time ? new Date(row.finish_time).toLocaleString() : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.completed ? 'success' : 'info'">
              {{ row.completed ? '已完成' : '未完成' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button-group>
              <el-button type="primary" @click="handleEdit(row)" size="small">编辑</el-button>
              <el-button 
                type="success" 
                :plain="!row.completed"
                @click="handleToggleStatus(row)"
                size="small"
              >
                {{ row.completed ? '取消完成' : '标记完成' }}
              </el-button>
              <el-button type="danger" @click="handleDelete(row)" size="small">删除</el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 已删除待办事项对话框 -->
      <el-dialog
        title="已删除的待办事项"
        v-model="showDeletedTodos"
        width="800px"
      >
        <div class="dialog-header">
          <el-button type="danger" @click="handlePermanentDeleteAll" :disabled="!deletedTodos.length">
            <el-icon><Delete /></el-icon>
            清空垃圾桶
          </el-button>
          <el-button type="danger" @click="handlePermanentDeleteBatch" :disabled="!selectedTodos.length">
            批量删除
          </el-button>
        </div>
        <el-table 
          :data="deletedTodos" 
          style="width: 100%"
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="title" label="标题" min-width="120"></el-table-column>
          <el-table-column prop="description" label="描述" min-width="180"></el-table-column>
          <el-table-column prop="deleted_at" label="删除时间" width="160">
            <template #default="{ row }">
              {{ row.deleted_at ? new Date(row.deleted_at).toLocaleString() : '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button-group>
                <el-button type="primary" @click="handleRestore(row)" size="small">恢复</el-button>
                <el-button type="danger" @click="handlePermanentDelete(row)" size="small">永久删除</el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-dialog>

      <!-- 添加/编辑待办对话框 -->
      <el-dialog
        :title="isEdit ? '编辑待办' : '添加待办'"
        v-model="dialogVisible"
        width="500px"
      >
        <el-form :model="todoForm" :rules="rules" ref="todoFormRef" label-width="80px">
          <el-form-item label="标题" prop="title">
            <el-input v-model="todoForm.title" placeholder="请输入待办事项标题"></el-input>
          </el-form-item>
          <el-form-item label="描述" prop="description">
            <el-input
              v-model="todoForm.description"
              type="textarea"
              :rows="3"
              placeholder="请输入待办事项描述"
            ></el-input>
          </el-form-item>
          <el-form-item label="开始时间" prop="start_time">
            <el-date-picker
              v-model="todoForm.start_time"
              type="datetime"
              placeholder="选择开始时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss.SSSZ"
            ></el-date-picker>
          </el-form-item>
          <el-form-item label="完成时间" prop="finish_time">
            <el-date-picker
              v-model="todoForm.finish_time"
              type="datetime"
              placeholder="选择完成时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss.SSSZ"
            ></el-date-picker>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="dialogVisible = false">取消</el-button>
            <el-button type="primary" @click="handleSubmit" :loading="submitting">
              {{ isEdit ? '保存' : '添加' }}
            </el-button>
          </span>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { Delete } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const store = useStore()
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const todoFormRef = ref(null)
const todos = ref([])

// 排序状态
const sortBy = ref('created_at')
const sortOrder = ref('descending')
const searchQuery = ref('')
const statusFilter = ref('all')

const todoForm = reactive({
  id: null,
  title: '',
  description: '',
  completed: false,
  start_time: '',
  finish_time: ''
})

const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度应在1-200个字符之间', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述长度不能超过500个字符', trigger: 'blur' }
  ]
}

// 获取待办事项列表
const fetchTodos = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/todos')
    todos.value = response.data
  } catch (error) {
    if (error.response?.status === 401) {
      store.commit('clearToken')
      router.push('/login')
    } else {
      ElMessage.error('获取待办事项失败')
    }
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  todoForm.id = null
  todoForm.title = ''
  todoForm.description = ''
  todoForm.completed = false
  todoForm.start_time = ''
  todoForm.finish_time = ''
  if (todoFormRef.value) {
    todoFormRef.value.resetFields()
  }
}

// 编辑待办事项
const handleEdit = (row) => {
  isEdit.value = true
  todoForm.id = row.id
  todoForm.title = row.title
  todoForm.description = row.description
  todoForm.completed = row.completed
  todoForm.start_time = row.start_time
  todoForm.finish_time = row.finish_time
  dialogVisible.value = true
}

// 切换待办事项状态
const handleToggleStatus = async (row) => {
  try {
    await axios.put(`/api/todos/${row.id}`, {
      title: row.title,
      description: row.description,
      completed: !row.completed
    })
    await fetchTodos()
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// 删除待办事项
const showDeletedTodos = ref(false)
const deletedTodos = ref([])

// 获取已删除的待办事项列表
const fetchDeletedTodos = async () => {
  try {
    const response = await axios.get('/api/todos/deleted')
    deletedTodos.value = response.data
  } catch (error) {
    ElMessage.error('获取已删除待办事项失败')
  }
}

// 恢复已删除的待办事项
const handleRestore = async (row) => {
  try {
    await axios.put(`/api/todos/${row.id}/restore`)
    await fetchDeletedTodos()
    await fetchTodos()
    ElMessage.success('恢复成功')
  } catch (error) {
    ElMessage.error('恢复失败')
  }
}

// 修改删除方法为软删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个待办事项吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/api/todos/${row.id}`)
    await fetchTodos()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 监听垃圾桶对话框打开
watch(showDeletedTodos, (newVal) => {
  if (newVal) {
    fetchDeletedTodos()
  }
})

// 提交表单
const handleSubmit = async () => {
  if (!todoFormRef.value) return
  
  try {
    await todoFormRef.value.validate()
    submitting.value = true
    
    if (isEdit.value) {
      const { title, description, completed, start_time, finish_time } = todoForm
      await axios.put(`/api/todos/${todoForm.id}`, { title, description, completed, start_time, finish_time })
    } else {
      const { title, description, completed, start_time, finish_time } = todoForm
      await axios.post('/api/todos', { title, description, completed, start_time, finish_time })
    }
    
    dialogVisible.value = false
    resetForm()
    await fetchTodos()
    ElMessage.success(isEdit.value ? '更新成功' : '添加成功')
  } catch (error) {
    if (error.response) {
      ElMessage.error(error.response.data.message || (isEdit.value ? '更新失败' : '添加失败'))
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('操作失败')
    }
  } finally {
    submitting.value = false
    isEdit.value = false
  }
}

// 监听对话框关闭
const handleDialogClose = () => {
  resetForm()
  isEdit.value = false
}

// 页面加载时获取待办事项列表
// 计算经过搜索和排序后的待办事项列表
const sortedTodos = computed(() => {
  let filtered = [...todos.value]
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(todo => 
      todo.title.toLowerCase().includes(query) ||
      (todo.description && todo.description.toLowerCase().includes(query))
    )
  }

  // 状态过滤
  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(todo => 
      statusFilter.value === 'completed' ? todo.completed : !todo.completed
    )
  }
  
  // 排序
  return filtered.sort((a, b) => {
    const aValue = a[sortBy.value]
    const bValue = b[sortBy.value]
    
    // 处理空值
    if (!aValue && !bValue) return 0
    if (!aValue) return sortOrder.value === 'ascending' ? 1 : -1
    if (!bValue) return sortOrder.value === 'ascending' ? -1 : 1
    
    // 比较值
    if (sortBy.value === 'title') {
      return sortOrder.value === 'ascending'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue)
    } else {
      const aDate = new Date(aValue)
      const bDate = new Date(bValue)
      return sortOrder.value === 'ascending'
        ? aDate - bDate
        : bDate - aDate
    }
  })
})

// 处理排序变更
const handleSortChange = ({ prop, order }) => {
  if (prop && order) {
    sortBy.value = prop
    sortOrder.value = order
  }
}

const selectedTodos = ref([])

// 处理表格选择变化
const handleSelectionChange = (selection) => {
  selectedTodos.value = selection
}

// 批量永久删除
const handlePermanentDeleteBatch = async () => {
  try {
    await ElMessageBox.confirm('确定要永久删除选中的待办事项吗？此操作不可恢复！', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const todoIds = selectedTodos.value.map(todo => todo.id)
    await axios.delete('/api/todos/deleted/permanent/batch', {
      data: { ids: todoIds }
    })
    await fetchDeletedTodos()
    ElMessage.success('批量删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || '批量删除失败')
    }
  }
}

// 清空垃圾桶
const handlePermanentDeleteAll = async () => {
  try {
    await ElMessageBox.confirm('确定要清空垃圾桶吗？此操作不可恢复！', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete('/api/todos/permanent/all')
    await fetchDeletedTodos()
    ElMessage.success('垃圾桶已清空')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败')
    }
  }
}

// 永久删除单个待办事项
const handlePermanentDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要永久删除这个待办事项吗？此操作不可恢复！', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await axios.delete(`/api/todos/deleted/permanent/${row.id}`)
    await fetchDeletedTodos()
    ElMessage.success('永久删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('永久删除失败')
    }
  }
}

onMounted(() => {
  fetchTodos()
})
</script>

<style scoped>
.todo-container {
  max-width: 1200px;
  margin: 20px auto;
  padding: 0 20px;
}

.todo-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.search-input {
  width: 300px;
}

.status-filter {
  width: 120px;
}
.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>