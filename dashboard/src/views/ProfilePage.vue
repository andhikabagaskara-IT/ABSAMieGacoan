<template>
  <div class="profile-page">
    <div class="section-title">
      <h2>Pengaturan Profil</h2>
      <p>Kelola informasi akun dan preferensi tampilan Anda.</p>
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
          <p class="help-text">Rekomendasi ukuran: 256x256px. Format: JPG, PNG, GIF.</p>
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
          <p class="help-text">Rekomendasi ukuran: 128x128px rasio 1:1. Format: PNG transparan disarankan.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const profileInput = ref(null)
const logoInput = ref(null)

const profileImage = ref('')
const companyLogo = ref('')

onMounted(() => {
  profileImage.value = localStorage.getItem('profileImage') || ''
  companyLogo.value = localStorage.getItem('companyLogo') || ''
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
    
    // Trigger event so other components update instantly
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

.profile-card {
  display: flex;
  flex-direction: column;
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

@media (max-width: 768px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
