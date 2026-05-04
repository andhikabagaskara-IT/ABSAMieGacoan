<template>
  <div class="profile-page">
    <div class="section-title">
      <h2>Pengaturan Profil</h2>
      <p>Kelola informasi akun, preferensi tampilan, dan info sistem.</p>
    </div>
    
    <div class="profile-grid">
      <!-- Profile Photo Settings -->
      <div class="card profile-card">
        <h3 class="card-title">Foto Profil</h3>
        <div class="card-body">
          <div class="avatar-preview">
            <img v-if="profileImage" :src="profileImage" alt="Profile" class="avatar-large" />
            <div v-else class="avatar-placeholder">A</div>
          </div>
          <div class="upload-actions">
            <input type="file" ref="profileInput" class="hidden-input" accept="image/*" @change="e => handleFileChange(e, 'profile')" />
            <button class="btn btn-primary" @click="$refs.profileInput.click()">Ubah Foto</button>
            <button class="btn btn-outline text-negative border-negative" @click="removeImage('profile')" v-if="profileImage">Hapus</button>
          </div>
          <p class="help-text">Rekomendasi ukuran: 256x256px. Format: JPG, PNG.</p>
        </div>
      </div>

      <!-- Company Logo Settings -->
      <div class="card profile-card">
        <h3 class="card-title">Logo Perusahaan</h3>
        <div class="card-body">
          <div class="logo-preview">
            <img v-if="companyLogo" :src="companyLogo" alt="Logo" class="logo-large" />
            <div v-else class="logo-placeholder">🍜</div>
          </div>
          <div class="upload-actions">
            <input type="file" ref="logoInput" class="hidden-input" accept="image/*" @change="e => handleFileChange(e, 'logo')" />
            <button class="btn btn-primary" @click="$refs.logoInput.click()">Ubah Logo</button>
            <button class="btn btn-outline text-negative border-negative" @click="removeImage('logo')" v-if="companyLogo">Hapus</button>
          </div>
          <p class="help-text">Rekomendasi rasio 1:1. Format: PNG transparan disarankan.</p>
        </div>
      </div>

      <!-- Setting Data Diri -->
      <div class="card form-card">
        <h3 class="card-title">Data Diri</h3>
        <form @submit.prevent="saveProfile" class="form-body">
          <div class="form-group">
            <label>Nama Lengkap</label>
            <input type="text" class="input-field" v-model="profileForm.name" placeholder="Nama Admin" />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" class="input-field" v-model="profileForm.email" placeholder="admin@gacoan.com" />
          </div>
          <div class="form-group">
            <label>Role</label>
            <input type="text" class="input-field" v-model="profileForm.role" disabled />
          </div>
          <button type="submit" class="btn btn-primary mt-3">Simpan Perubahan</button>
        </form>
      </div>

      <!-- Setting Password -->
      <div class="card form-card">
        <h3 class="card-title">Ubah Password</h3>
        <form @submit.prevent="changePassword" class="form-body">
          <div class="form-group">
            <label>Password Saat Ini</label>
            <input type="password" class="input-field" v-model="passwordForm.current" placeholder="••••••••" required />
          </div>
          <div class="form-group">
            <label>Password Baru</label>
            <input type="password" class="input-field" v-model="passwordForm.new" placeholder="••••••••" required />
          </div>
          <div class="form-group">
            <label>Konfirmasi Password Baru</label>
            <input type="password" class="input-field" v-model="passwordForm.confirm" placeholder="••••••••" required />
          </div>
          <button type="submit" class="btn btn-primary mt-3">Perbarui Password</button>
        </form>
      </div>

      <!-- Info/About Sistem -->
      <div class="card info-card" style="grid-column: 1 / -1;">
        <h3 class="card-title">Tentang Sistem</h3>
        <div class="system-info">
          <div class="info-row">
            <span class="info-label">Nama Sistem</span>
            <span class="info-value">Gacoan Insight - Sentiment Management Platform</span>
          </div>
          <div class="info-row">
            <span class="info-label">Versi</span>
            <span class="info-value">v1.2.0</span>
          </div>
          <div class="info-row">
            <span class="info-label">Metode ML</span>
            <span class="info-value">Support Vector Machine (SVM), Naive Bayes, SMOTE, Stratified K-Fold</span>
          </div>
          <div class="info-row">
            <span class="info-label">Ekstraksi Aspek</span>
            <span class="info-value">Latent Dirichlet Allocation (LDA)</span>
          </div>
          <div class="info-row">
            <span class="info-label">Pengembang</span>
            <span class="info-value">Maulana Andhika | Informatics Engineering UNAIR</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'

const profileInput = ref(null)
const logoInput = ref(null)

const profileImage = ref('')
const companyLogo = ref('')

const profileForm = reactive({
  name: 'Admin',
  email: 'admin@gacoan.com',
  role: 'Administrator'
})

const passwordForm = reactive({
  current: '',
  new: '',
  confirm: ''
})

onMounted(() => {
  profileImage.value = localStorage.getItem('profileImage') || ''
  companyLogo.value = localStorage.getItem('companyLogo') || ''
  
  const savedProfile = localStorage.getItem('userProfile')
  if (savedProfile) {
    const parsed = JSON.parse(savedProfile)
    profileForm.name = parsed.name || 'Admin'
    profileForm.email = parsed.email || 'admin@gacoan.com'
  }
})

const handleFileChange = (e, type) => {
  const file = e.target.files[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (event) => {
    const base64String = event.target.result
    if (type === 'profile') {
      profileImage.value = base64String
      localStorage.setItem('profileImage', base64String)
    } else {
      companyLogo.value = base64String
      localStorage.setItem('companyLogo', base64String)
    }
    
    window.dispatchEvent(new Event('profile-updated'))
  }
  reader.readAsDataURL(file)
}

const removeImage = (type) => {
  if (type === 'profile') {
    profileImage.value = ''
    localStorage.removeItem('profileImage')
  } else {
    companyLogo.value = ''
    localStorage.removeItem('companyLogo')
  }
  window.dispatchEvent(new Event('profile-updated'))
}

const saveProfile = () => {
  localStorage.setItem('userProfile', JSON.stringify(profileForm))
  alert('Data diri berhasil disimpan!')
}

const changePassword = () => {
  if (passwordForm.new !== passwordForm.confirm) {
    alert('Konfirmasi password tidak cocok!')
    return
  }
  // Simplified logic for demo
  alert('Password berhasil diperbarui!')
  passwordForm.current = ''
  passwordForm.new = ''
  passwordForm.confirm = ''
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

.section-title h2 {
  margin: 0 0 0.25rem 0;
  font-size: 1.25rem;
  color: var(--text-primary);
}

.section-title p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.profile-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.card-title {
  margin: 0 0 1.5rem 0;
  font-size: 1.125rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border);
  padding-bottom: 1rem;
}

.card-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.avatar-preview, .logo-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: var(--bg-subtle);
  border: 2px dashed var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.logo-preview {
  border-radius: var(--radius-md);
}

.avatar-large {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.logo-large {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 0.5rem;
}

.avatar-placeholder {
  font-size: 3rem;
  font-weight: 700;
  color: var(--text-secondary);
}

.logo-placeholder {
  font-size: 3rem;
}

.upload-actions {
  display: flex;
  gap: 1rem;
}

.hidden-input {
  display: none;
}

.help-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-align: center;
  margin: 0;
}

.border-negative {
  border-color: var(--negative);
}

.text-negative {
  color: var(--negative);
}

.text-negative:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

/* Forms */
.form-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.mt-3 {
  margin-top: 0.75rem;
}

/* Info System */
.system-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  padding: 0.75rem;
  border-bottom: 1px solid var(--border);
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  width: 150px;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.info-value {
  flex: 1;
  color: var(--text-primary);
  font-size: 0.875rem;
}

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  
  .info-row {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .info-label {
    width: 100%;
  }
}
</style>
