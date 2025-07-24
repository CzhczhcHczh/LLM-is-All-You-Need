import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router.js'

const app = createApp(App)
const pinia = createPinia()

// 确保这些组件被正确注册
import { 
  ElCollapse, 
  ElCollapseItem, 
  ElAlert, 
  ElEmpty, 
  ElTag, 
  ElButton 
} from 'element-plus'

// 单独注册折叠面板组件（如果全局导入有问题）
app.component('ElCollapse', ElCollapse)
app.component('ElCollapseItem', ElCollapseItem)
app.component('ElAlert', ElAlert)
app.component('ElEmpty', ElEmpty)
app.component('ElTag', ElTag)
app.component('ElButton', ElButton)

// Register Element Plus icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')

