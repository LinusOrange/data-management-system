<script setup>
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAppData } from './composables/useAppData'

const route = useRoute()
const { state, loadAll } = useAppData()

onMounted(loadAll)
</script>

<template>
  <main class="page">
    <header class="topbar">
      <h1>票据数据对账系统</h1>
      <nav class="nav">
        <router-link to="/dashboard" :class="{ active: route.path === '/dashboard' }">系统看板</router-link>
        <router-link to="/upload" :class="{ active: route.path === '/upload' }">上传文件对账</router-link>
        <router-link to="/reconciliation" :class="{ active: route.path === '/reconciliation' }">对账页面</router-link>
        <router-link to="/database" :class="{ active: route.path === '/database' }">数据库管理</router-link>
        <router-link to="/files" :class="{ active: route.path === '/files' }">文件与条目管理</router-link>
      </nav>
    </header>

    <p v-if="state.message" class="msg">{{ state.message }}</p>

    <router-view />
  </main>
</template>
