import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getTrainingLogs } from '../api/index.js'

export const useTrainingStore = defineStore('training', () => {
  const rewardData = ref([])
  const taskStatus = ref('pending')
  const loading = ref(false)
  const error = ref('')
  let ws = null

  async function loadHistory(taskId) {
    loading.value = true
    error.value = ''
    try {
      const { data } = await getTrainingLogs(taskId)
      rewardData.value = data.map((item) => ({
        episode: item.episode,
        reward: item.reward,
        epsilon: null,
        avgReward: item.avg_reward,
      }))
    } catch (err) {
      error.value = err.response?.data?.detail || '加载历史数据失败'
    } finally {
      loading.value = false
    }
  }

  function connect(taskId) {
    disconnect()
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = protocol + '//' + location.host + '/ws/' + taskId
    ws = new WebSocket(url)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'reward_update') {
        rewardData.value.push({
          episode: data.episode,
          reward: data.reward,
          epsilon: data.epsilon,
        })
      } else if (data.type === 'status_change') {
        taskStatus.value = data.status
      }
    }

    ws.onerror = () => {
      error.value = 'WebSocket 连接异常'
    }

    ws.onclose = () => {
      ws = null
    }
  }

  function disconnect() {
    if (ws) {
      ws.close()
      ws = null
    }
  }

  function clearData() {
    rewardData.value = []
    taskStatus.value = 'pending'
    error.value = ''
  }

  return { rewardData, taskStatus, loading, error, loadHistory, connect, disconnect, clearData }
})
