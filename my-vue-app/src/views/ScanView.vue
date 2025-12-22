<script setup>
import { onMounted, onBeforeUnmount, ref, computed } from 'vue';
import { Html5Qrcode } from 'html5-qrcode';
import { useRoute, useRouter } from 'vue-router';
import StatusDetails from '../components/StatusDetails.vue';
import { useDeviceSettings, buildHeaders } from '../composables/useDeviceSettings';
import { humanTime } from '../utils/time';

const API_BASE = '/api/tablet';
const route = useRoute();
const router = useRouter();
const mode = route.query.mode || 'register';

const { deviceToken, deviceId } = useDeviceSettings();
const scannedQr = ref('');
const manualQr = ref('');
const status = ref(null);
const statusError = ref('');
const statusLoading = ref(false);
const successMessage = ref('');
const successAction = ref('');
const countdown = ref(null);
let countdownTimer = null;
let returnTimer = null;
let html5QrcodeInstance = null;

const actionsAvailable = computed(() => status.value?.actions || []);

const resetSuccess = () => {
  successMessage.value = '';
  successAction.value = '';
  countdown.value = null;
  if (countdownTimer) clearInterval(countdownTimer);
  if (returnTimer) clearTimeout(returnTimer);
};

const startReturn = (seconds = 3) => {
  countdown.value = seconds;
  countdownTimer = setInterval(() => {
    countdown.value -= 1;
    if (countdown.value <= 0) {
      clearInterval(countdownTimer);
    }
  }, 1000);
  returnTimer = setTimeout(() => router.push('/'), seconds * 1000);
};

const extendReturn = (extra = 60) => {
  if (returnTimer) clearTimeout(returnTimer);
  if (countdownTimer) clearInterval(countdownTimer);
  startReturn(extra);
};

const stopScanner = () => {
  if (html5QrcodeInstance) {
    html5QrcodeInstance.stop().catch(() => {});
  }
};

const startScanner = async () => {
  try {
    const cameras = await Html5Qrcode.getCameras();
    if (!cameras.length) {
      statusError.value = 'Brak dostępnej kamery';
      return;
    }
    html5QrcodeInstance = new Html5Qrcode('reader');
    await html5QrcodeInstance.start(
      cameras[0].id,
      { fps: 10, qrbox: 240 },
      (decodedText) => onScan(decodedText),
    );
  } catch (err) {
    statusError.value = err.message || 'Nie udało się uruchomić skanera';
  }
};

const fetchStatus = async (qrToken) => {
  statusLoading.value = true;
  statusError.value = '';
  status.value = null;
  try {
    const params = new URLSearchParams({ qr: qrToken });
    if (deviceId.value) params.set('device', deviceId.value);
    const resp = await fetch(`${API_BASE}/status/?${params.toString()}`, {
      headers: buildHeaders(deviceToken.value),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || data.message || 'Błąd statusu');
    status.value = data;
  } catch (err) {
    statusError.value = err.message;
  } finally {
    statusLoading.value = false;
  }
};

const sendEvent = async (eventType) => {
  if (!scannedQr.value) return;
  statusLoading.value = true;
  statusError.value = '';
  successMessage.value = '';
  successAction.value = '';
  try {
    const resp = await fetch(`${API_BASE}/events/`, {
      method: 'POST',
      headers: buildHeaders(deviceToken.value, { 'Content-Type': 'application/json' }),
      body: JSON.stringify({
        qr: scannedQr.value,
        event_type: eventType,
        device_id: deviceId.value || undefined,
      }),
    });
    const data = await resp.json();
    if (!resp.ok && resp.status !== 200 && resp.status !== 201) {
      throw new Error(data.detail || data.message || 'Błąd zapisu');
    }
    successMessage.value = data.message || 'Zapisano';
    successAction.value = eventType;
    startReturn(3);
  } catch (err) {
    statusError.value = err.message;
  } finally {
    statusLoading.value = false;
  }
};

const onScan = (decodedText) => {
  resetSuccess();
  scannedQr.value = decodedText;
  manualQr.value = decodedText;
  stopScanner();
  fetchStatus(decodedText);
};

const submitManual = () => {
  if (!manualQr.value) return;
  resetSuccess();
  scannedQr.value = manualQr.value;
  fetchStatus(manualQr.value);
};

const actionLabel = {
  CHECK_IN: 'Wejście',
  CHECK_OUT: 'Wyjście',
  BREAK_START: 'Przerwa',
  BREAK_END: 'Koniec przerwy',
  TOILET: 'Toaleta',
};

const actionTone = {
  CHECK_IN: 'success',
  CHECK_OUT: 'danger',
  BREAK_START: 'warning',
  BREAK_END: 'success',
  TOILET: 'secondary',
};

onMounted(() => {
  startScanner();
});

onBeforeUnmount(() => {
  stopScanner();
  resetSuccess();
});
</script>

<template>
  <div class="grid two">
    <div class="card">
      <h2>Skanuj kod QR</h2>
      <div id="reader" class="status-box" style="min-height:260px; display:flex; align-items:center; justify-content:center;">
        <div class="muted">Oczekiwanie na kamerę…</div>
      </div>
      <div style="margin-top:12px;">
        <label class="label">Token ręcznie</label>
        <input class="input" v-model="manualQr" placeholder="Wpisz token, jeśli kamera jest niedostępna" />
        <button class="btn primary" style="margin-top:8px" @click="submitManual">Użyj tokenu</button>
      </div>
      <p v-if="statusError" class="alert" style="margin-top:12px;">{{ statusError }}</p>
    </div>

    <div class="card" v-if="scannedQr || status">
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px;">
        <span class="badge blue">Token: {{ scannedQr || manualQr }}</span>
        <span class="badge gray" v-if="mode === 'status'">Tryb: status</span>
        <span class="badge gray" v-else>Tryb: rejestracja</span>
      </div>

      <StatusDetails v-if="status" :status="status" />

      <div v-if="status && !successMessage" style="margin-top:14px;">
        <h4>Dostępne akcje</h4>
        <div class="actions-grid" style="margin-top:8px;">
          <button
            v-for="action in actionsAvailable"
            :key="action"
            class="btn"
            :class="actionTone[action] || 'primary'"
            :disabled="statusLoading"
            @click="sendEvent(action)"
          >
            {{ actionLabel[action] || action }}
          </button>
        </div>
      </div>

      <div v-if="successMessage" style="margin-top:16px;">
        <div class="success-box">
          <div class="small muted">Rozpoczęto</div>
          <h3 style="margin:6px 0;">{{ actionLabel[successAction] || successAction }}</h3>
          <div class="muted">{{ successMessage }}</div>
          <div class="status-grid" style="margin-top:12px;">
            <div class="status-box">
              <div class="small muted">Czas pracy</div>
              <div style="font-weight:700;">{{ status?.work_minutes }} min</div>
            </div>
            <div class="status-box">
              <div class="small muted">Przerwy</div>
              <div style="font-weight:700;">{{ status?.break_minutes }} min</div>
            </div>
            <div class="status-box">
              <div class="small muted">Ostatnie zdarzenie</div>
              <div style="font-weight:700;">{{ humanTime(status?.last_event_timestamp) }}</div>
            </div>
          </div>
          <div class="timer-row" style="margin-top:12px;">
            <button class="btn primary" style="max-width:220px;" @click="router.push('/')">
              Zamknij <span v-if="countdown">({{ countdown }}s)</span>
            </button>
            <button class="btn secondary" style="max-width:120px;" @click="extendReturn(60)">+60s</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
