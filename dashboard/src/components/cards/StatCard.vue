<template>
  <div class="glass-card stat-card">
    <div class="stat-content">
      <div class="stat-label">{{ label }}</div>
      <div class="stat-value" :class="valueClass">{{ displayValue }}</div>
      <div v-if="subtitle" class="stat-subtitle">{{ subtitle }}</div>
    </div>
    <div class="stat-icon" :class="iconClass">
      <component :is="icon" v-if="icon" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [Number, String], required: true },
  subtitle: { type: String, default: '' },
  icon: { type: [Object, Function], default: null },
  type: { type: String, default: 'default' } // 'default', 'positive', 'negative'
})

const valueClass = computed(() => {
  if (props.type === 'positive') return 'text-positive'
  if (props.type === 'negative') return 'text-negative'
  return 'text-primary'
})

const iconClass = computed(() => {
  return `icon-${props.type}`
})

const displayValue = computed(() => {
  if (typeof props.value === 'number') {
    return new Intl.NumberFormat('id-ID').format(props.value)
  }
  return props.value
})
</script>

<style scoped>
.stat-card {
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.stat-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.stat-subtitle {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon svg {
  width: 24px;
  height: 24px;
}

.icon-default {
  background-color: rgba(3, 169, 244, 0.1);
  color: var(--primary);
}

.icon-positive {
  background-color: rgba(16, 185, 129, 0.1);
  color: var(--positive);
}

.icon-negative {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--negative);
}
</style>
