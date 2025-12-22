<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router';
import StatusDetails from '../components/StatusDetails.vue';
import { useDeviceSettings, buildHeaders } from '../composables/useDeviceSettings';

const API_BASE = '/api/tablet';
const route = useRoute();
const { deviceToken, deviceId } = useDeviceSettings();

const qr = ref(route.query.qr || '');
const status = ref(null);
const loading = ref(false);
const error = ref('');

const fetchStatus = async () => {
  if (!qr.value) {
    error.value = 'Podaj token QR';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const params = new URLSearchParams({ qr: qr.value });
    if (deviceId.value) params.set('device', deviceId.value);
    const resp = await fetch(`${API_BASE}/status/?${params.toString()}`, {
      headers: buildHeaders(deviceToken.value),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || data.message || 'Błąd statusu');
    status.value = data;
  } catch (err) {
    status.value = null;
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

if (qr.value) {
  fetchStatus();
}
</script>

<template>
  <div class="grid two">
    <div class="card">
      <h2>Status pracownika</h2>
      <label class="label" for="qr">Token QR</label>
      <input id="qr" class="input" v-model="qr" placeholder="Wklej token pracownika" />
      <button class="btn primary" style="margin-top:12px" :disabled="loading" @click="fetchStatus">
        {{ loading ? 'Pobieram...' : 'Pobierz status' }}
      </button>
      <p class="muted" style="margin-top:8px;">Nagłówek <code>X-Device-Token</code> jest wymagany.</p>
      <p v-if="error" class="alert" style="margin-top:12px;">{{ error }}</p>
    </div>

    <StatusDetails v-if="status" :status="status" />
  </div>
</template>
