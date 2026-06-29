import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

export function listTasks() {
  return api.get('/tasks')
}

export function createTask(payload) {
  return api.post('/tasks', payload)
}

export function getTask(taskId) {
  return api.get(`/tasks/${taskId}`)
}

export function deleteTask(taskId) {
  return api.delete(`/tasks/${taskId}`)
}

export function startTask(taskId) {
  return api.post(`/training/${taskId}/start`)
}

export function pauseTask(taskId) {
  return api.post(`/training/${taskId}/pause`)
}

export function cancelTask(taskId) {
  return api.post(`/training/${taskId}/cancel`)
}

export function getTrainingLogs(taskId) {
  return api.get(`/training/${taskId}/logs`)
}

export default api
