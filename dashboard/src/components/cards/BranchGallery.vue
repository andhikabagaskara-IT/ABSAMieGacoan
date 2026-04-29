<template>
  <div class="card gallery-card">
    <div class="card-header">
      <MapPin class="icon text-primary" />
      <h3 class="card-title">Galeri Cabang Surabaya</h3>
    </div>
    
    <p class="description">Klik pada cabang untuk melihat lokasi di Google Maps.</p>
    
    <div class="gallery-grid">
      <a 
        v-for="(branch, index) in cabangList" 
        :key="index"
        :href="branch.url"
        target="_blank"
        rel="noopener noreferrer"
        class="branch-item"
      >
        <div class="image-wrapper">
          <img :src="`https://placehold.co/400x300/F8FAFC/03A9F4?text=${encodeURIComponent(branch.nama.replace('Mie Gacoan - ', ''))}`" :alt="branch.nama" class="branch-image" />
          <div class="overlay">
            <ExternalLink class="overlay-icon" />
          </div>
        </div>
        <div class="branch-info">
          <span class="branch-name">{{ branch.nama }}</span>
        </div>
      </a>
    </div>
  </div>
</template>

<script setup>
import { MapPin, ExternalLink } from 'lucide-vue-next'

const cabangList = [
  {"nama": "Mie Gacoan - Wiyung",           "url": "https://maps.app.goo.gl/WC2cPgABq7CiAtaX8"},
  {"nama": "Mie Gacoan - Manyar Kertoarjo", "url": "https://maps.app.goo.gl/nB2fYBQn2m3tk3v38"},
  {"nama": "Mie Gacoan - Merr",             "url": "https://maps.app.goo.gl/N8JBzqk4pXSxdYTH7"},
  {"nama": "Mie Gacoan - Ahmad Yani",       "url": "https://maps.app.goo.gl/xSKJt44PdHSfjp5t7"},
  {"nama": "Mie Gacoan - Margorejo",        "url": "https://maps.app.goo.gl/Y12rmMEQFobX3AUF9"},
  {"nama": "Mie Gacoan - Ambengan",         "url": "https://maps.app.goo.gl/vsj2LQevkFfRPuMo9"},
  {"nama": "Mie Gacoan - Mayjen Sungkono",  "url": "https://maps.app.goo.gl/YGydbVMPLZi345Ut5"},
  {"nama": "Mie Gacoan - Ir Soekarno",      "url": "https://maps.app.goo.gl/eDgrHwHQRUQyAC287"},
  {"nama": "Mie Gacoan - Kenjeran",         "url": "https://maps.app.goo.gl/ydkAr6sDRt748sgPA"},
  {"nama": "Mie Gacoan - Kenjeran 2",       "url": "https://maps.app.goo.gl/RnrkJRoZdewbZ1N98"},
  {"nama": "Mie Gacoan - Ngagel",           "url": "https://maps.app.goo.gl/WpyX1s9AkWekAKo59"},
  {"nama": "Mie Gacoan - Manukan",          "url": "https://maps.app.goo.gl/AxDcp6hgcL6NFg9q8"}
]
</script>

<style scoped>
.gallery-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
  color: var(--text-primary);
}

.description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-top: -0.5rem;
  margin-bottom: 1rem;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.branch-item {
  text-decoration: none;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  transition: transform var(--transition-fast);
}

.branch-item:hover {
  transform: translateY(-5px);
}

.image-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.branch-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.branch-item:hover .branch-image {
  transform: scale(1.05);
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(3, 169, 244, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.branch-item:hover .overlay {
  opacity: 1;
}

.overlay-icon {
  color: white;
  width: 32px;
  height: 32px;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.branch-info {
  text-align: center;
}

.branch-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

@media (max-width: 576px) {
  .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }
}
</style>
