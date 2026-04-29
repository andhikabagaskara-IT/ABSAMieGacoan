<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-circle circle-1"></div>
      <div class="bg-circle circle-2"></div>
      <div class="bg-circle circle-3"></div>
    </div>

    <div class="login-card glass-card">
      <div class="login-header">
        <span class="logo-emoji">🍜</span>
        <h1>GACOAN ANALYTICS</h1>
        <p>Sentiment Analysis by Andhika IT</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">
            <Mail class="field-icon" />
            Email
          </label>
          <input 
            id="email"
            type="email" 
            v-model="email" 
            placeholder="admin@gacoan.com" 
            class="input-field"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">
            <Lock class="field-icon" />
            Password
          </label>
          <div class="password-wrapper">
            <input 
              id="password"
              :type="showPassword ? 'text' : 'password'" 
              v-model="password" 
              placeholder="Masukkan password" 
              class="input-field"
              required
            />
            <button type="button" class="toggle-pw" @click="showPassword = !showPassword">
              <Eye v-if="!showPassword" class="pw-icon" />
              <EyeOff v-else class="pw-icon" />
            </button>
          </div>
        </div>

        <div class="form-options">
          <label class="checkbox-wrapper">
            <input type="checkbox" v-model="rememberMe" />
            <span>Ingat saya</span>
          </label>
          <a href="#" class="forgot-link">Lupa password?</a>
        </div>

        <button type="submit" class="btn btn-primary login-btn" :class="{ loading: isLoading }">
          <LogIn class="btn-icon" v-if="!isLoading" />
          <span class="spinner" v-else></span>
          {{ isLoading ? 'Masuk...' : 'Masuk' }}
        </button>

        <p v-if="errorMsg" class="error-msg">
          <AlertCircle class="error-icon" />
          {{ errorMsg }}
        </p>
      </form>

      <div class="login-footer">
        <p>© 2026 Gacoan Insight — ABSA Mie Gacoan Surabaya</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Mail, Lock, Eye, EyeOff, LogIn, AlertCircle } from 'lucide-vue-next'

const router = useRouter()

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  errorMsg.value = ''
  isLoading.value = true

  // Simulate login delay
  await new Promise(resolve => setTimeout(resolve, 1200))

  // Simple hardcoded auth for demo
  if (email.value === 'admin@gacoan.com' && password.value === 'admin123') {
    localStorage.setItem('gacoan_user', JSON.stringify({
      name: 'Admin Gacoan',
      email: email.value,
      role: 'Administrator',
      avatar: '🍜',
      loginTime: new Date().toISOString()
    }))
    router.push('/')
  } else {
    errorMsg.value = 'Email atau password salah. Coba: admin@gacoan.com / admin123'
  }

  isLoading.value = false
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0D1B2A 0%, #1B3A5C 50%, #0D1B2A 100%);
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

/* Animated background */
.login-bg { position: absolute; inset: 0; pointer-events: none; }
.bg-circle {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.3;
  animation: float 8s ease-in-out infinite;
}
.circle-1 { width: 400px; height: 400px; background: var(--primary); top: -100px; right: -100px; animation-delay: 0s; }
.circle-2 { width: 300px; height: 300px; background: var(--accent); bottom: -80px; left: -80px; animation-delay: 2s; }
.circle-3 { width: 200px; height: 200px; background: var(--primary-light); top: 50%; left: 50%; animation-delay: 4s; }

@keyframes float {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-20px) scale(1.05); }
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 2.5rem;
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  border-radius: 16px;
  position: relative;
  z-index: 1;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-emoji {
  font-size: 3rem;
  display: block;
  margin-bottom: 0.5rem;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.login-header h1 {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: 1px;
  background: var(--gradient-accent);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.login-header p {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
}

.login-form { display: flex; flex-direction: column; gap: 1.25rem; }

.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group label { display: flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); }
.field-icon { width: 14px; height: 14px; }

.password-wrapper { position: relative; }
.toggle-pw { position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-secondary); padding: 0.25rem; cursor: pointer; }
.toggle-pw:hover { color: var(--primary); }
.pw-icon { width: 16px; height: 16px; }

.form-options { display: flex; justify-content: space-between; align-items: center; }
.checkbox-wrapper { display: flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; color: var(--text-secondary); cursor: pointer; }
.checkbox-wrapper input { accent-color: var(--primary); }
.forgot-link { font-size: 0.8rem; color: var(--primary); font-weight: 500; }
.forgot-link:hover { color: var(--accent); }

.login-btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 0.95rem;
  font-weight: 600;
  gap: 0.5rem;
  border-radius: var(--radius-md);
  transition: all 0.3s;
}
.login-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(3, 169, 244, 0.35); }
.login-btn.loading { opacity: 0.8; pointer-events: none; }
.btn-icon { width: 18px; height: 18px; }

.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.error-msg {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--negative);
  font-size: 0.8rem;
  background: rgba(239, 68, 68, 0.08);
  padding: 0.6rem 0.75rem;
  border-radius: var(--radius-md);
  border: 1px solid rgba(239, 68, 68, 0.2);
}
.error-icon { width: 16px; height: 16px; flex-shrink: 0; }

.login-footer {
  text-align: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}
.login-footer p { font-size: 0.7rem; color: var(--text-secondary); }

@media (max-width: 480px) {
  .login-card { padding: 1.5rem; }
}
</style>
