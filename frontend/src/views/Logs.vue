<template>
  <div>
    <h2>训练日志</h2>
    <el-select v-model="selectedTaskId" placeholder="选择任务" style="width: 240px; margin-bottom: 16px" @change="loadLogs">
      <el-option v-for="task in tasks" :key="task.id" :label="task.id + ' - ' + task.name" :value="task.id" />
    </el-select>

    <el-table :data="logs" stripe style="width: 100%">
      <el-table-column prop="episode" label="Episode" width="100" />
      <el-table-column prop="step" label="Step" width="100" />
      <el-table-column prop="reward" label="Reward" width="120" />
      <el-table-column prop="avg_reward" label="Avg Reward" width="120" />
      <el-table-column prop="created_at" label="时间">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getApiErrorMessage, getTrainingLogs, listTasks } from '../api/index.js'

const tasks = ref([])
const logs = ref([])
const selectedTaskId = ref(null)

function formatTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString()
}

async function loadLogs() {
  if (!selectedTaskId.value) return
  try {
    const { data } = await getTrainingLogs(selectedTaskId.value)
    logs.value = data
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, '加载日志失败'))
  }
}

onMounted(async () => {
  try {
    const { data } = await listTasks()
    tasks.value = data
  } catch (error) {
    ElMessage.error(getApiErrorMessage(error, '加载任务失败'))
  }
})
</script>
