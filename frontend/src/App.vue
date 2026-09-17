<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const activeMenu = computed(() => {
  const p = route.path
  if (p.startsWith('/trips')) return '/trips'
  if (p.startsWith('/create')) return '/create'
  return '/'
})

function onCommand(cmd: string) {
  if (cmd === 'logout') {
    store.logout()
    router.push('/login')
  } else if (cmd === 'profile') {
    router.push('/trips')
  }
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="container topbar-inner">
        <div class="brand" @click="router.push('/')">
          <span class="logo">✈️</span>
          <span class="brand-name">TravelAI</span>
          <span class="brand-sub">智能旅行规划助手</span>
        </div>

        <el-menu :default-active="activeMenu" mode="horizontal" :router="true" class="nav">
          <el-menu-item index="/">首页</el-menu-item>
          <el-menu-item index="/create">生成行程</el-menu-item>
          <el-menu-item index="/trips">我的行程</el-menu-item>
        </el-menu>

        <div class="account">
          <template v-if="store.token">
            <el-dropdown @command="onCommand">
              <span class="user-chip">
                <el-icon><User /></el-icon>
                {{ store.user?.username || '我的账号' }}
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">我的行程</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" size="small" @click="router.push('/login')">
              登录 / 注册
            </el-button>
          </template>
        </div>
      </div>
    </header>

    <main class="container main">
      <router-view />
    </main>

    <footer class="footer muted">
      <div class="container">
        TravelAI · LangGraph 多智能体 + RAG 知识库 · 行程数据仅用于演示
      </div>
    </footer>
  </div>
</template>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.topbar {
  background: #fff;
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 10;
}

.topbar-inner {
  display: flex;
  align-items: center;
  gap: 24px;
}

.brand {
  display: flex;
  align-items: baseline;
  gap: 8px;
  cursor: pointer;
  white-space: nowrap;
}

.logo {
  font-size: 22px;
}

.brand-name {
  font-size: 18px;
  font-weight: 800;
  color: var(--brand);
}

.brand-sub {
  font-size: 12px;
  color: var(--muted);
}

.nav {
  flex: 1;
  border-bottom: none;
}

.user-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: var(--text);
  font-size: 14px;
}

.main {
  flex: 1;
  padding: 24px 16px 40px;
}

.footer {
  border-top: 1px solid var(--border);
  padding: 16px 0;
  font-size: 12px;
  text-align: center;
  background: #fff;
}
</style>
