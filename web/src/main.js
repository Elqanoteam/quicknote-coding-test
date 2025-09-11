import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './pages/Home.vue'
import NoteDetail from './pages/NoteDetail.vue'
import './styles.css'

// Router configuration
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/note/:id',
      name: 'NoteDetail',
      component: NoteDetail,
      props: true
    }
  ]
})

// Create and mount app
const app = createApp(App)
app.use(router)
app.mount('#app')
