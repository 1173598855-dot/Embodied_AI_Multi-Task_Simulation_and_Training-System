<template>
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <h2>任务管理</h2>
      <el-button type="primary" @click="showForm = true">新建任务</el-button>
    </div>

    <el-table :data="tasks" stripe style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="env_type" label="环境" width="100" />
      <el-table-column prop="env_name" label="环境名" width="140" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_reward" label="总Reward" width="100" />
      <el-table-column label="操作" width="220">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="startTask(row.id)" :disabled="row.status === 'running'">
            启动
          </el-button>
          <el-button size="small" @click="$router.push('/training/' + row.id)">监控</el-button>
          <el-popconfirm title="确认删除?" @confirm="deleteTask(row.id)">
            <template #reference>
              <el-button size="small" type="danger">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <TaskForm v-if="showForm" :show="showForm" @close="showForm = false" @created="loadTasks" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'
import TaskForm from '../components/TaskForm.vue'
import { ElMessage } from 'element-plus'

const tasks = ref([])
const showForm = ref(false)

function statusType(status) {
  const map = { pending: 'info', running: '', completed: 'success', paused: 'warning', failed: 'danger' }
  return map[status] || 'info'
}

async function loadTasks() {
  try {
    const { data } = await api.get('/tasks')
    tasks.value = data
  } catch (e) {
    ElMessage.error('加载任务失败')
  }
}

async function startTask(id) {
  try {
    await api.post('/training/' + id + '/start')
    ElMessage.success('任务已入队')
    loadTasks()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '启动失败')
  }
}

async function deleteTask(id) {
  try {
    await api.delete('/tasks/' + id)
    ElMessage.success('已删除')
    loadTasks()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(loadTasks)
</script>