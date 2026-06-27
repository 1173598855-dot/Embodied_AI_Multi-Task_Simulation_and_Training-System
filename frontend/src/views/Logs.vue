<template>
  <div>
    <h2>训练日志</h2>
    <el-select v-model="selectedTaskId" placeholder="选择任务" style="width: 240px; margin-bottom: 16px" @change="loadLogs">
      <el-option v-for="t in tasks" :key="t.id" :label="t.id + ' - ' + t.name" :value="t.id" />
    </el-select>

    <el-table :data="logs" stripe style="width: 100%">
      <el-table-column prop="episode" label="Episode" width="100" />
      <el-table-column prop="reward" label="Reward" width="120" />
      <el-table-column prop="created_at" label="时间">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

const tasks = ref([])
const logs = ref([])
const selectedTaskId = ref(null)

function formatTime(t) {
  if (!t) return ''
  return new Date(t).toLocaleString()
}

async function loadLogs() {
  if (!selectedTaskId.value) return
  const { data } = await api.get('/training/' + selectedTaskId.value + '/logs')
  logs.value = data
}

onMounted(async () => {
  const { data } = await api.get('/tasks')
  tasks.value = data
})
</script>