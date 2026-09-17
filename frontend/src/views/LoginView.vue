<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const store = useUserStore()

const activeTab = ref<'login' | 'register'>('login')
const loading = ref(false)

const loginForm = reactive({ identifier: '', password: '' })
const registerForm = reactive({ username: '', email: '', password: '', confirm: '' })

const redirect = (route.query.redirect as string) || '/trips'

async function onLogin() {
  if (!loginForm.identifier.trim() || !loginForm.password) {
    ElMessage.warning('请输入账号和密码')
    return
  }
  loading.value = true
  try {
    const ok = await store.login(loginForm.identifier.trim(), loginForm.password)
    if (ok) {
      ElMessage.success('登录成功')
      router.replace(redirect)
    }
  } catch {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}

async function onRegister() {
  if (registerForm.username.trim().length < 2) {
    ElMessage.warning('用户名至少 2 个字符')
    return
  }
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(registerForm.email)) {
    ElMessage.warning('请输入有效的邮箱')
    return
  }
  if (registerForm.password.length < 6) {
    ElMessage.warning('密码至少 6 位')
    return
  }
  if (registerForm.password !== registerForm.confirm) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  loading.value = true
  try {
    const ok = await store.register({
      username: registerForm.username.trim(),
      email: registerForm.email.trim(),
      password: registerForm.password,
    })
    if (ok) {
      ElMessage.success('注册成功，已自动登录')
      router.replace(redirect)
    }
  } catch {
    /* 拦截器已提示 */
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-wrap">
    <div class="auth-card card">
      <div class="brand-center">
        <span class="logo">✈️</span>
        <span class="brand-name">TravelAI</span>
      </div>

      <el-tabs v-model="activeTab" class="auth-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form label-position="top" @submit.prevent="onLogin">
            <el-form-item label="用户名 / 邮箱">
              <el-input
                v-model="loginForm.identifier"
                placeholder="用户名或邮箱"
                autocomplete="username"
                @keyup.enter="onLogin"
              />
            </el-form-item>
            <el-form-item label="密码">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                show-password
                autocomplete="current-password"
                @keyup.enter="onLogin"
              />
            </el-form-item>
            <el-button type="primary" :loading="loading" class="full" @click="onLogin">
              登录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form label-position="top" @submit.prevent="onRegister">
            <el-form-item label="用户名">
              <el-input v-model="registerForm.username" placeholder="2-50 个字符" />
            </el-form-item>
            <el-form-item label="邮箱">
              <el-input v-model="registerForm.email" placeholder="you@example.com" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="至少 6 位"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码">
              <el-input
                v-model="registerForm.confirm"
                type="password"
                placeholder="再次输入密码"
                show-password
              />
            </el-form-item>
            <el-button type="primary" :loading="loading" class="full" @click="onRegister">
              注册并登录
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<style scoped>
.auth-wrap {
  display: flex;
  justify-content: center;
  padding-top: 32px;
}
.auth-card {
  width: 400px;
  max-width: 100%;
  padding: 28px;
}
.brand-center {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}
.logo {
  font-size: 22px;
}
.brand-name {
  font-size: 20px;
  font-weight: 800;
  color: var(--brand);
}
.auth-tabs {
  margin-top: 4px;
}
.full {
  width: 100%;
}
</style>
