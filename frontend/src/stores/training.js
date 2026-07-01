import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getApiErrorMessage, getTrainingLogs } from '../api/index.js'

export const useTrainingStore = defineStore('training', () => {
  const rewardData = ref([])
  const taskStatus = ref('created')
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
      error.value = getApiErrorMessage(err, '加载历史数据失败')
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
      if (data.type === 'episode_completed' || data.type === 'reward_update') {
        rewardData.value.push({
          episode: data.episode,
          reward: data.reward,
          epsilon: data.epsilon,
          avgReward: data.avg_reward ?? data.avgReward,
        })
      } else if (data.type === 'status_changed' || data.type === 'status_change') {
        taskStatus.value = data.status
      } else if (data.type === 'task_failed') {
        taskStatus.value = 'failed'
        error.value = data.error || '训练任务失败'
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
    taskStatus.value = 'created'
    error.value = ''
  }

  return { rewardData, taskStatus, loading, error, loadHistory, connect, disconnect, clearData }
})
