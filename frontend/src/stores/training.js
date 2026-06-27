import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useTrainingStore = defineStore('training', () => {
  const rewardData = ref([])
  const taskStatus = ref('pending')
  let ws = null

  function connect(taskId) {
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

    ws.onclose = () => { ws = null }
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
  }

  return { rewardData, taskStatus, connect, disconnect, clearData }
})