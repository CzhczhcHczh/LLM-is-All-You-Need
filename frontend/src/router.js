import { createRouter, createWebHistory } from 'vue-router'
import Phase1 from './components/Phase1.vue'
import Phase2 from './components/Phase2.vue'
import Phase3 from './components/Phase3.vue'
import Phase4 from './components/Phase4.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('./App.vue'), // 或者创建单独的Home组件
    meta: { title: '首页' }
  },
  {
    path: '/',
    redirect: '/phase1'
  },
  {
    path: '/phase1',
    name: 'Phase1',
    component: Phase1,
    meta: { title: '职位搜索' }
  },
  {
    path: '/phase2',
    name: 'Phase2',
    component: Phase2,
    meta: { title: '简历制作' }
  },
  {
    path: '/phase3',
    name: 'Phase3',
    component: Phase3,
    meta: { title: 'HR模拟' }
  },
  {
    path: '/phase4',
    name: 'Phase4',
    component: Phase4,
    meta: { title: '面试安排' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

