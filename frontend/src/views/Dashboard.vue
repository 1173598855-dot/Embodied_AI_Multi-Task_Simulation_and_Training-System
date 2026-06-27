<template>
  <div>
    <h2>仪表盘</h2>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>任务总数</template>
          <div style="font-size: 32px; font-weight: bold">{{ stats.total }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>运行中</template>
          <div style="font-size: 32px; font-weight: bold; color: #409eff">{{ stats.running }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>已完成</template>
          <div style="font-size: 32px; font-weight: bold; color: #67c23a">{{ stats.completed }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <template #header>失败</template>
          <div style="font-size: 32px; font-weight: bold; color: #f56c6c">{{ stats.failed }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api/index.js'

const stats = ref({ total: 0, running: 0, completed: 0, failed: 0 })

onMounted(async () => {
  try {
    const { data } = await api.get('/tasks')
    stats.value.total = data.length
    stats.value.running = data.filter(t => t.status === 'running').length
    stats.value.completed = data.filter(t => t.status === 'completed').length
    stats.value.failed = data.filter(t => t.status === 'failed').length
  } catch (e) {
    console.error('Failed to load stats', e)
  }
})
</script>
