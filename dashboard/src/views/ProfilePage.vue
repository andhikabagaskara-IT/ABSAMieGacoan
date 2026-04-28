<template>
  <div class="profile-page">
    <div class="section-title">
      <h2>👤 Profil Pengguna</h2>
      <p>Kelola informasi akun dan preferensi dashboard Anda.</p>
    </div>

    <div class="profile-grid">
      <!-- Left: User Card -->
      <div class="card user-card">
        <div class="avatar-section">
          <div class="avatar">{{ user.avatar }}</div>
          <div class="user-info">
            <h3>{{ user.name }}</h3>
            <span class="role-badge">{{ user.role }}</span>
          </div>
        </div>

        <div class="info-list">
          <div class="info-item">
            <Mail class="info-icon" />
            <div>
              <span class="info-label">Email</span>
              <span class="info-value">{{ user.email }}</span>
            </div>
          </div>
          <div class="info-item">
            <Clock class="info-icon" />
            <div>
              <span class="info-label">Login Terakhir</span>
              <span class="info-value">{{ formatDate(user.loginTime) }}</span>
            </div>
          </div>
          <div class="info-item">
            <Shield class="info-icon" />
            <div>
              <span class="info-label">Status</span>
              <span class="info-value status-active">● Aktif</span>
            </div>
          </div>
        </div>

        <button class="btn btn-outline logout-btn" @click="handleLogout">
          <LogOut class="btn-icon" />
          Logout
        </button>
      </div>

      <!-- Right: Settings Cards -->
      <div class="settings-column">
        <!-- Edit Profile -->
        <div class="card settings-card">
          <h4><UserCog class="card-icon" /> Edit Profil</h4>
          <form @submit.prevent="saveProfile" class="settings-form">
            <div class="form-group">
              <label>Nama Lengkap</label>
              <input type="text" v-model="editName" class="input-field" />
            </div>
            <div class="form-group">
              <label>Email</label>
              <input type="email" v-model="editEmail" class="input-field" />
            </div>
            <div class="form-group">
              <label>Role</label>
              <select v-model="editRole" class="input-field">
                <option>Administrator</option>
                <option>Manager</option>
                <option>Analyst</option>
                <option>Viewer</option>
              </select>
            </div>
            <button type="submit" class="btn btn-primary save-btn">
              <Save class="btn-icon" />
              Simpan Perubahan
            </button>
            <p v-if="saveSuccess" class="success-msg">
              <CheckCircle class="success-icon" />
              Profil berhasil diperbarui!
            </p>
          </form>
        </div>

        <!-- Dashboard Stats -->
        <div class="card stats-card">
          <h4><BarChart3 class="card-icon" /> Statistik Dashboard</h4>
          <div class="stats-grid">
            <div class="stat-box">
              <span class="stat-number">51.885</span>
              <span class="stat-label">Total Ulasan</span>
            </div>
            <div class="stat-box">
              <span class="stat-number">12</span>
              <span class="stat-label">Cabang Aktif</span>
            </div>
            <div class="stat-box">
              <span class="stat-number">4</span>
              <span class="stat-label">Aspek LDA</span>
            </div>
            <div class="stat-box">
              <span class="stat-number">99.62%</span>
              <span class="stat-label">Akurasi SVM</span>
            </div>
          </div>
        </div>

        <!-- System Info -->
        <div class="card system-card">
          <h4><Info class="card-icon" /> Informasi Sistem</h4>
          <div class="sys-list">
            <div class="sys-row">
              <span>Platform</span>
              <span class="sys-value">VueJS Dashboard v1.0</span>
            </div>
            <div class="sys-row">
              <span>Data Source</span>
              <span class="sys-value">dashboard_data.json</span>
            </div>
            <div class="sys-row">
              <span>Model Terbaik</span>
              <span class="sys-value badge-accent-sm">SVM Linear</span>
            </div>
            <div class="sys-row">
              <span>SMOTE</span>
              <span class="sys-value badge-primary-sm">Aktif (K=4)</span>
            </div>
            <div class="sys-row">
              <span>Last Data Sync</span>
              <span class="sys-value">{{ formatDate(new Date().toISOString()) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Mail, Clock, Shield, LogOut, UserCog, Save, CheckCircle, 
  BarChart3, Info 
} from 'lucide-vue-next'

const router = useRouter()

const user = ref({
  name: 'Admin Gacoan',
  email: 'admin@gacoan.com',
  role: 'Administrator',
  avatar: '🍜',
  loginTime: new Date().toISOString()
})

const editName = ref('')
const editEmail = ref('')
const editRole = ref('')
const saveSuccess = ref(false)

onMounted(() => {
  const stored = localStorage.getItem('gacoan_user')
  if (stored) {
    const parsed = JSON.parse(stored)
    user.value = { ...user.value, ...parsed }
  }
  editName.value = user.value.name
  editEmail.value = user.value.email
  editRole.value = user.value.role
})

const saveProfile = () => {
  user.value.name = editName.value
  user.value.email = editEmail.value
  user.value.role = editRole.value
  localStorage.setItem('gacoan_user', JSON.stringify(user.value))
  saveSuccess.value = true
  setTimeout(() => { saveSuccess.value = false }, 3000)
}

const handleLogout = () => {
  localStorage.removeItem('gacoan_user')
  router.push('/login')
}

const formatDate = (iso) => {
  if (!iso) return '-'
  return new Date(iso).toLocaleString('id-ID', {
    day: 'numeric', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  })
}
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

.section-title h2 { margin: 0 0 0.25rem 0; font-size: 1.25rem; }
.section-title p { margin: 0; font-size: 0.875rem; color: var(--text-secondary); }

.profile-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1.5rem;
  align-items: start;
}

/* User Card */
.user-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  text-align: center;
}

.avatar-section { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; }
.avatar {
  width: 80px; height: 80px;
  background: var(--gradient-accent);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 2.5rem;
  box-shadow: 0 4px 20px rgba(3, 169, 244, 0.3);
}
.user-info h3 { margin: 0; font-size: 1.125rem; }
.role-badge {
  display: inline-block;
  padding: 0.2rem 0.75rem;
  background: rgba(3, 169, 244, 0.1);
  color: var(--primary-dark);
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  margin-top: 0.25rem;
}

.info-list { display: flex; flex-direction: column; gap: 0.75rem; text-align: left; }
.info-item { display: flex; align-items: center; gap: 0.75rem; }
.info-icon { width: 18px; height: 18px; color: var(--primary); flex-shrink: 0; }
.info-label { display: block; font-size: 0.7rem; color: var(--text-secondary); font-weight: 500; }
.info-value { display: block; font-size: 0.85rem; font-weight: 500; }
.status-active { color: var(--positive); }

.logout-btn { width: 100%; gap: 0.5rem; color: var(--negative); border-color: rgba(239, 68, 68, 0.3); }
.logout-btn:hover { background: rgba(239, 68, 68, 0.05); border-color: var(--negative); }

/* Settings Cards */
.settings-column { display: flex; flex-direction: column; gap: 1.5rem; }

.settings-card h4, .stats-card h4, .system-card h4 {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 1rem; margin: 0 0 1.25rem 0;
}
.card-icon { width: 18px; height: 18px; color: var(--primary); }

.settings-form { display: flex; flex-direction: column; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
.form-group label { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); }

.save-btn { gap: 0.4rem; font-size: 0.85rem; margin-top: 0.5rem; }
.btn-icon { width: 16px; height: 16px; }

.success-msg {
  display: flex; align-items: center; gap: 0.4rem;
  color: var(--positive); font-size: 0.8rem;
  background: rgba(16, 185, 129, 0.08);
  padding: 0.5rem 0.75rem; border-radius: var(--radius-md);
  border: 1px solid rgba(16, 185, 129, 0.2);
  animation: fadeIn 0.3s ease;
}
.success-icon { width: 16px; height: 16px; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

/* Stats */
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.stat-box {
  background: var(--bg-subtle); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 1rem; text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-box:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.stat-number { display: block; font-size: 1.5rem; font-weight: 800; background: var(--gradient-accent); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.stat-label { display: block; font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.25rem; font-weight: 500; }

/* System Info */
.sys-list { display: flex; flex-direction: column; gap: 0.6rem; }
.sys-row { display: flex; justify-content: space-between; align-items: center; padding: 0.4rem 0; border-bottom: 1px solid var(--border); font-size: 0.825rem; }
.sys-row:last-child { border-bottom: none; }
.sys-row span:first-child { color: var(--text-secondary); }
.sys-value { font-weight: 500; }
.badge-accent-sm { background: rgba(236, 64, 122, 0.1); color: var(--accent); padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }
.badge-primary-sm { background: rgba(3, 169, 244, 0.1); color: var(--primary-dark); padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; }

@media (max-width: 768px) {
  .profile-grid { grid-template-columns: 1fr; }
}
</style>
