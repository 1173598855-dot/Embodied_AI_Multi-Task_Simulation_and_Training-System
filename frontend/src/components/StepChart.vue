<template>
  <div ref="chartRef" style="width: 100%; height: 300px"></div>
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
  chart.setOption({
    title: { text: 'Epsilon 衰减', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: props.data.map(d => d.episode), name: 'Episode' },
    yAxis: { type: 'value', name: 'Epsilon', max: 1.0 },
    series: [
      { type: 'line', data: props.data.map(d => d.epsilon), smooth: true, lineStyle: { color: '#67c23a', width: 2 }, areaStyle: { color: 'rgba(103,194,58,0.1)' } },
    ],
    grid: { left: 60, right: 20, top: 40, bottom: 40 },
  })
}
</script>
