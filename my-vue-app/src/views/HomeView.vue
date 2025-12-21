<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useDeviceSettings } from '../composables/useDeviceSettings'

const router = useRouter()
const { deviceToken, deviceId, hasAuth, reset } = useDeviceSettings()

const message = ref('')
const messageType = ref('neutral')

const canNavigate = computed(() => hasAuth.value)

const showMessage = (text, type = 'neutral') => {
  message.value = text
  messageType.value = type
  setTimeout(() => (message.value = ''), 4000)
}

const onSave = () => {
  if (!deviceToken.value) {
    showMessage('Podaj token urządzenia', 'error')
    return
  }
  showMessage('Dane zapisane', 'success')
}

const onClear = () => {
  reset()
  showMessage('Wyczyszczono zapisane dane', 'success')
}

const navigate = (path) => router.push(path)
</script>

<template>
  <section class="panel">
    <div class="panel__header">
      <div>
        <p class="eyebrow">Konsola tabletu</p>
        <h1>Konfiguracja urządzenia</h1>
        <p class="muted">Ustaw token i opcjonalny identyfikator urządzenia.</p>
      </div>
      <div class="chips">
        <span class="chip" :class="{ 'chip--active': hasAuth }">Token</span>
        <span class="chip" :class="{ 'chip--active': !!deviceId }">Device ID</span>
      </div>
    </div>

    <div class="grid">
      <label class="field">
        <span>Token urządzenia</span>
        <input v-model.trim="deviceToken" type="text" placeholder="np. 7a9b..." />
      </label>
      <label class="field">
        <span>ID urządzenia (opcjonalnie)</span>
        <input v-model.trim="deviceId" type="text" placeholder="np. kiosk-01" />
      </label>
    </div>

    <div class="actions">
      <button class="btn btn--primary" type="button" @click="onSave">Zapisz</button>
      <button class="btn" type="button" @click="onClear">Wyczyść</button>
    </div>

    <div v-if="message" class="alert" :class="`alert--${messageType}`">{{ message }}</div>
  </section>

  <section class="panel panel--secondary">
    <div class="panel__header">
      <h2>Operacje</h2>
      <p class="muted">Przejdź do skanowania lub podglądu statusu.</p>
    </div>

    <div class="menu-grid">
      <button class="tile" :disabled="!canNavigate" @click="navigate('/scan')">
        <div>
          <p class="eyebrow">Skanowanie</p>
          <h3>Kod QR</h3>
        </div>
        <span class="pill">Rozpocznij</span>
      </button>

      <button class="tile" :disabled="!canNavigate" @click="navigate('/status')">
        <div>
          <p class="eyebrow">Status</p>
          <h3>API /api/tablet/status/</h3>
        </div>
        <span class="pill">Sprawdź</span>
      </button>

      <button class="tile" @click="navigate('/schedule')">
        <div>
          <p class="eyebrow">Harmonogram</p>
          <h3>Lista zadań</h3>
        </div>
        <span class="pill">Podgląd</span>
      </button>

      <button class="tile" @click="navigate('/reports')">
        <div>
          <p class="eyebrow">Raporty</p>
          <h3>Zdarzenia</h3>
        </div>
        <span class="pill">Podgląd</span>
      </button>
    </div>
  </section>
</template>
