<template>
  <div>
    <div style="display: flex; justify-content: space-between; margin-bottom: 16px">
      <h2>训练监控 — 任务 #{{ taskId }}</h2>
      <el-tag :type="statusType(store.taskStatus)" size="large">{{ store.taskStatus }}</el-tag>
    </div>

    <el-empty v-if="store.rewardData.length === 0" description="等待训练数据..." />

    <template v-else>
      <el-card shadow="never" style="margin-bottom: 16px">
        <RewardChart :data="store.rewardData" />
      </el-card>
      <el-card shadow="never">
        <StepChart :data="store.rewardData" />
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTrainingStore } from '../stores/training.js'
import RewardChart from '../components/RewardChart.vue'
import StepChart from '../components/StepChart.vue'

const route = useRoute()
const store = useTrainingStore()
const taskId = computed(() => route.params.id)

function statusType(status) {
  const map = { pending: 'info', running: '', completed: 'success', failed: 'danger' }
  return map[status] || 'info'
}

onMounted(() => {
  store.clearData()
  store.connect(taskId.value)
})

onUnmounted(() => {
  store.disconnect()
})
</script>
