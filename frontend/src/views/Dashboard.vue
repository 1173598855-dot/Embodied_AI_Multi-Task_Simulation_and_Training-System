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
          <template #header>异常/暂停</template>
          <div style="font-size: 32px; font-weight: bold; color: #f56c6c">{{ stats.problematic }}</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getApiErrorMessage, listTasks } from '../api/index.js'

const stats = ref({ total: 0, running: 0, completed: 0, problematic: 0 })

onMounted(async () => {
  try {
    const { data } = await listTasks()
    stats.value.total = data.length
    stats.value.running = data.filter((task) => ['queued', 'running'].includes(task.status)).length
    stats.value.completed = data.filter((task) => task.status === 'completed').length
    stats.value.problematic = data.filter((task) => ['failed', 'paused', 'canceled'].includes(task.status)).length
  } catch (error) {
    console.error(getApiErrorMessage(error, '加载统计失败'))
  }
})
</script>
