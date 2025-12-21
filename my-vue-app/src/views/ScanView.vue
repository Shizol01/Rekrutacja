<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useDeviceSettings } from '../composables/useDeviceSettings'

const router = useRouter()
const { deviceToken, deviceId } = useDeviceSettings()

const scannerContainerId = 'qr-reader'
const html5QrCodeRef = ref(null)
const scanning = ref(false)
const scriptLoading = ref(false)
const error = ref('')
const success = ref('')
const manualToken = ref('')
const autoBackTimer = ref(null)

const clearMessages = () => {
  error.value = ''
  success.value = ''
}

const loadScannerLibrary = () =>
  new Promise((resolve, reject) => {
    if (window.Html5Qrcode) {
      resolve(window.Html5Qrcode)
      return
    }
    if (scriptLoading.value) return
    scriptLoading.value = true
    const script = document.createElement('script')
    script.src = 'https://unpkg.com/html5-qrcode@2.3.8/dist/html5-qrcode.min.js'
    script.async = true
    script.onload = () => {
      scriptLoading.value = false
      if (window.Html5Qrcode) {
        resolve(window.Html5Qrcode)
      } else {
        reject(new Error('Nie udało się załadować biblioteki'))
      }
    }
    script.onerror = () => {
      scriptLoading.value = false
      reject(new Error('Błąd pobierania biblioteki skanera'))
    }
    document.body.appendChild(script)
  })

const startScanner = async () => {
  clearMessages()
  if (!deviceToken.value) {
    error.value = 'Brak tokenu urządzenia — ustaw go w konfiguracji.'
    return
  }
  try {
    const Html5Qrcode = await loadScannerLibrary()
    if (html5QrCodeRef.value) {
      await stopScanner()
    }
    html5QrCodeRef.value = new Html5Qrcode(scannerContainerId)
    scanning.value = true
    await html5QrCodeRef.value.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: 250 },
      onScanSuccess,
      (err) => console.debug('QR error', err)
    )
  } catch (err) {
    error.value = err?.message || 'Nie udało się uruchomić skanera'
  }
}

const stopScanner = async () => {
  if (!html5QrCodeRef.value || !scanning.value) return
  try {
    await html5QrCodeRef.value.stop()
    await html5QrCodeRef.value.clear()
  } catch (err) {
    console.warn('Stop scanner error', err)
  } finally {
    scanning.value = false
  }
}

const onScanSuccess = async (decodedText) => {
  await stopScanner()
  await submitEvent(decodedText)
}

const submitEvent = async (tokenOverride) => {
  clearMessages()
  if (!deviceToken.value) {
    error.value = 'Brak tokenu urządzenia — ustaw go w konfiguracji.'
    return
  }
  const payload = {
    token: tokenOverride || manualToken.value,
    created_at: new Date().toISOString(),
  }

  if (!payload.token) {
    error.value = 'Brak tokenu QR — podaj ręcznie lub zeskanuj.'
    return
  }

  try {
    const response = await fetch('/api/tablet/events/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Device-Token': deviceToken.value,
        ...(deviceId.value ? { 'X-Device-Id': deviceId.value } : {}),
      },
      body: JSON.stringify(payload),
    })

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || 'Błąd zapisu zdarzenia')
    }

    success.value = 'Zdarzenie zapisane'
    manualToken.value = ''
    scheduleBack()
  } catch (err) {
    error.value = err?.message || 'Nie udało się zapisać zdarzenia'
  }
}

const scheduleBack = () => {
  if (autoBackTimer.value) clearTimeout(autoBackTimer.value)
  autoBackTimer.value = setTimeout(() => router.push('/'), 2000)
}

onMounted(() => {
  startScanner()
})

onBeforeUnmount(async () => {
  if (autoBackTimer.value) clearTimeout(autoBackTimer.value)
  await stopScanner()
})
</script>

<template>
  <section class="panel">
    <div class="panel__header">
      <div>
        <p class="eyebrow">Skanowanie QR</p>
        <h1>Skanuj kod lub podaj ręcznie</h1>
        <p class="muted">Wymagany zapisany token urządzenia (X-Device-Token).</p>
      </div>
      <div class="chips">
        <span class="chip" :class="{ 'chip--active': scanning }">Kamera</span>
        <span class="chip" :class="{ 'chip--active': !!manualToken }">Manual</span>
      </div>
    </div>

    <div class="scanner">
      <div :id="scannerContainerId" class="scanner__preview" aria-label="Podgląd kamery"></div>
      <div class="scanner__fallback">
        <p class="muted">Jeśli kamera jest niedostępna, wprowadź token ręcznie.</p>
        <label class="field">
          <span>Token z QR</span>
          <input
            v-model.trim="manualToken"
            type="text"
            placeholder="np. EVENT-12345"
            :disabled="!!success"
          />
        </label>
        <div class="actions">
          <button class="btn btn--primary" type="button" :disabled="!!success" @click="submitEvent()">
            Wyślij zdarzenie
          </button>
          <button class="btn" type="button" :disabled="!!success" @click="startScanner">Uruchom ponownie kamerę</button>
        </div>
      </div>
    </div>

    <div v-if="success" class="alert alert--success">{{ success }}</div>
    <div v-else-if="error" class="alert alert--error">{{ error }}</div>
  </section>
</template>
