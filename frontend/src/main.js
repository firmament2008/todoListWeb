import { createApp } from 'vue'
import { createStore } from 'vuex'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'

// 创建Vuex store
const store = createStore({
  state() {
    return {}
  },
  mutations: {}
})

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/todos'
    },
    {
      path: '/todos',
      component: () => import('./views/TodoList.vue')
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  next()
})

// 创建Vue应用
const app = createApp(App)

// 使用插件
app.use(store)
app.use(router)
app.use(ElementPlus)

// 挂载应用
app.mount('#app')