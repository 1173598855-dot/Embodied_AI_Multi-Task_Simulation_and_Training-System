<template>
  <el-dialog v-model="visible" title="创建训练任务" width="500px" @close="$emit('close')">
    <el-form :model="form" label-width="100px">
      <el-form-item label="任务名称">
        <el-input v-model="form.name" placeholder="如: CartPole 训练" />
      </el-form-item>
      <el-form-item label="环境类型">
        <el-select v-model="form.env_type" style="width: 100%">
          <el-option label="Gym" value="gym" />
          <el-option label="PyBullet (机器人)" value="robot" disabled />
        </el-select>
      </el-form-item>
      <el-form-item label="环境名称">
        <el-input v-model="form.env_name" placeholder="如: CartPole-v1" />
      </el-form-item>
      <el-form-item label="训练轮数">
        <el-input-number v-model="form.config.episodes" :min="10" :max="10000" />
      </el-form-item>
      <el-form-item label="学习率">
        <el-input-number v-model="form.config.lr" :min="0.001" :max="1.0" :step="0.01" />
      </el-form-item>
      <el-form-item label="折扣因子">
        <el-input-number v-model="form.config.gamma" :min="0.1" :max="1.0" :step="0.01" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('close')">取消</el-button>
      <el-button type="primary" @click="submit" :loading="loading">创建</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive } from 'vue'
import api from '../api/index.js'
import { ElMessage } from 'element-plus'

const props = defineProps({ show: Boolean })
const emit = defineEmits(['close', 'created'])
const visible = ref(props.show)
const loading = ref(false)

const form = reactive({
  name: '',
  env_type: 'gym',
  env_name: 'CartPole-v1',
  algo: 'q_learning',
  config: { episodes: 500, lr: 0.1, gamma: 0.99, epsilon: 1.0 },
})

async function submit() {
  if (!form.name) {
    ElMessage.warning('请输入任务名称')
    return
  }
  loading.value = true
  try {
    await api.post('/tasks', form)
    ElMessage.success('任务创建成功')
    emit('created')
    emit('close')
  } catch (e) {
    ElMessage.error('创建失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}
</script>