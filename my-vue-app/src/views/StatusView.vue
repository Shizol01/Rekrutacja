<script setup>
import { ref } from 'vue'

import { formatDateTime, formatDuration } from '../utils/time'
import { useDeviceSettings } from '../composables/useDeviceSettings'

const { deviceToken, deviceId } = useDeviceSettings()

const loading = ref(false)
const statusData = ref(null)
const error = ref('')

const fetchStatus = async () => {
  if (!deviceToken.value) {
    error.value = 'Najpierw ustaw token urządzenia.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const response = await fetch('/api/tablet/status/', {
      headers: {
        'X-Device-Token': deviceToken.value,
        ...(deviceId.value ? { 'X-Device-Id': deviceId.value } : {}),
      },
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || 'Błąd pobierania statusu')
    }

    statusData.value = await response.json()
  } catch (err) {
    error.value = err?.message || 'Nie udało się pobrać statusu'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="panel">
    <div class="panel__header">
      <div>
        <p class="eyebrow">Status API</p>
        <h1>/api/tablet/status/</h1>
        <p class="muted">Wyświetl odpowiedź serwera dla zapisanych nagłówków.</p>
      </div>
      <button class="btn btn--primary" type="button" :disabled="loading" @click="fetchStatus">
        {{ loading ? 'Ładowanie…' : 'Odśwież' }}
      </button>
    </div>

    <div v-if="error" class="alert alert--error">{{ error }}</div>

    <div v-if="statusData" class="status-grid">
      <div>
        <p class="eyebrow">device_id</p>
        <p class="mono">{{ statusData.device_id || '—' }}</p>
      </div>
      <div>
        <p class="eyebrow">heartbeat_at</p>
        <p class="mono">{{ formatDateTime(statusData.heartbeat_at) }}</p>
      </div>
      <div>
        <p class="eyebrow">uptime_seconds</p>
        <p class="mono">{{ formatDuration(statusData.uptime_seconds) }}</p>
      </div>
      <div>
        <p class="eyebrow">events_total</p>
        <p class="mono">{{ statusData.events_total ?? '—' }}</p>
      </div>
      <div>
        <p class="eyebrow">meta</p>
        <pre class="mono block">{{ JSON.stringify(statusData.meta || {}, null, 2) }}</pre>
      </div>
    </div>
    <p v-else class="muted">Brak danych — odśwież, aby pobrać status.</p>
  </section>
</template>
