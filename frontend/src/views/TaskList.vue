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
      <el-table-column prop="env_name" label="环境名称" width="160" />
      <el-table-column label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="total_reward" label="总奖励" width="100" />
      <el-table-column label="操作" width="360">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="startTask(row.id)" :disabled="!canStart(row.status)">
            启动
          </el-button>
          <el-button size="small" type="warning" @click="pauseTask(row.id)" :disabled="!canPause(row.status)">
            暂停
          </el-button>
          <el-button size="small" type="danger" @click="cancelTask(row.id)" :disabled="!canCancel(row.status)">
            取消
          </el-button>
          <el-button size="small" @click="$router.push('/training/' + row.id)">监控</el-button>
          <el-popconfirm title="确认删除?" @confirm="deleteTaskById(row.id)">
            <template #reference>
              <el-button size="small" type="danger" :disabled="!canDelete(row.status)">删除</el-button>
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
import { ElMessage } from 'element-plus'
import TaskForm from '../components/TaskForm.vue'
import {
  cancelTask as apiCancelTask,
  deleteTask as apiDeleteTask,
  getApiErrorMessage,
  listTasks,
  pauseTask as apiPauseTask,
  startTask as apiStartTask,
} from '../api/index.js'

const tasks = ref([])
const showForm = ref(false)

const statusLabels = {
  created: '已创建',
  queued: '排队中',
  running: '运行中',
  paused: '已暂停',
  completed: '已完成',
  failed: '失败',
  canceled: '已取消',
}

function statusLabel(status) {
  return statusLabels[status] || status
}

function statusType(status) {
  const map = { created: 'info', queued: 'info', running: '', completed: 'success', paused: 'warning', failed: 'danger', canceled: 'info' }
  return map[status] || 'info'
}

function canStart(status) {
  return ['created', 'paused', 'failed'].includes(status)
}

function canPause(status) {
  return ['queued', 'running'].includes(status)
}

function canCancel(status) {
  return ['created', 'queued', 'running', 'paused', 'failed'].includes(status)
}

function canDelete(status) {
  return ['created', 'completed', 'failed', 'canceled'].includes(status)
}

async function loadTasks() {
  try {
    const { data } = await listTasks()
    tasks.value = data
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, '加载任务失败'))
  }
}

async function startTask(id) {
  try {
    await apiStartTask(id)
    ElMessage.success('任务已入队')
    await loadTasks()
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, '启动失败'))
  }
}

async function pauseTask(id) {
  try {
    await apiPauseTask(id)
    ElMessage.success('任务已暂停')
    await loadTasks()
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, '暂停失败'))
  }
}

async function cancelTask(id) {
  try {
    await apiCancelTask(id)
    ElMessage.success('任务已取消')
    await loadTasks()
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, '取消失败'))
  }
}

async function deleteTaskById(id) {
  try {
    await apiDeleteTask(id)
    ElMessage.success('已删除')
    await loadTasks()
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, '删除失败'))
  }
}

onMounted(loadTasks)
</script>
