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

const option = computed(() => {
  // 从scores对象中提取所有键值对
  const dimensions = Object.entries(props.scores);
  
  // 限制最多显示5个维度，避免雷达图过于复杂
  const limitedDimensions = dimensions.slice(0, 5);
  
  // 创建通用维度名称（维度1，维度2，...）
  const indicators = limitedDimensions.map((item, index) => {
    return { name: `维度${index + 1}`, max: 100 };
  });
  
  // 提取值
  const values = limitedDimensions.map(item => item[1] || 0);
  
  return {
    tooltip: {
      formatter: (params) => {
        // 在tooltip中显示实际的维度名称和值
        const data = params.data;
        let result = `${data.name}<br/>`;
        limitedDimensions.forEach((dim, index) => {
          // 将键名格式化为更可读的文本
          const readableName = dim[0]
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
          result += `${readableName}: ${data.value[index]}<br/>`;
        });
        return result;
      }
    },
    radar: {
      indicator: indicators,
      radius: 110
    },
    series: [{
      type: 'radar',
      data: [{
        value: values,
        name: '能力评估'
      }]
    }]
  };
})
</script>