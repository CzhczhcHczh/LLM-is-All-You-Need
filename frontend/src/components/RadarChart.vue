<template>
  <v-chart :option="option" autoresize style="height:320px;width:100%;" />
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import VChart from 'vue-echarts'
import { RadarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

use([RadarChart, TitleComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  scores: {
    type: Object,
    required: true
  }
})

const option = computed(() => ({
  tooltip: {},
  radar: {
    indicator: [
      { name: '工作经验匹配度', max: 100 },
      { name: '技能专业程度', max: 100 },
      { name: '业绩表现', max: 100 },
      { name: '职业稳定性', max: 100 },
      { name: '简历专业性', max: 100 }
    ],
    radius: 110
  },
  series: [{
    type: 'radar',
    data: [{
      value: [
        props.scores.experience_match || 0,
        props.scores.skills_proficiency || 0,
        props.scores.performance_results || 0,
        props.scores.career_stability || 0,
        props.scores.resume_professionalism || 0
      ],
      name: '能力雷达'
    }]
  }]
}))
</script>