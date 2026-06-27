<template>
  <div ref="chartRef" style="width: 100%; height: 400px"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({ data: { type: Array, default: () => [] } })
const chartRef = ref(null)
let chart = null

onMounted(() => {
  chart = echarts.init(chartRef.value)
  updateChart()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  chart?.dispose()
})

watch(() => props.data, updateChart, { deep: true })

function updateChart() {
  if (!chart) return
  const episodes = props.data.map(d => d.episode)
  const rewards = props.data.map(d => d.reward)

  const avgRewards = rewards.map((_, i) => {
    const start = Math.max(0, i - 19)
    const slice = rewards.slice(start, i + 1)
    return slice.reduce((a, b) => a + b, 0) / slice.length
  })

  chart.setOption({
    title: { text: 'Reward 曲线', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, data: ['Reward', 'Average (20)'] },
    xAxis: { type: 'category', data: episodes, name: 'Episode' },
    yAxis: { type: 'value', name: 'Reward' },
    series: [
      { name: 'Reward', type: 'scatter', data: rewards, symbolSize: 3, itemStyle: { color: '#409eff' } },
      { name: 'Average (20)', type: 'line', data: avgRewards, smooth: true, lineStyle: { color: '#e6a23c', width: 2 } },
    ],
    grid: { left: 60, right: 20, top: 40, bottom: 50 },
  })
}
</script>
