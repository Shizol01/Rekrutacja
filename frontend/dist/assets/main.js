import {
  createApp,
  ref,
  computed,
  onMounted,
  onBeforeUnmount,
} from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js';
import { createRouter, createWebHistory, useRouter, useRoute } from 'https://unpkg.com/vue-router@4/dist/vue-router.esm-browser.js';

const API_BASE = '/api/tablet';
const QR_LIB_URL = 'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js';

const actionMeta = {
  CHECK_IN: { label: '▶ Rozpocznij pracę', tone: 'success' },
  BREAK_START: { label: '☕ Rozpocznij przerwę', tone: 'warning' },
  BREAK_END: { label: '▶ Zakończ przerwę', tone: 'success' },
  TOILET: { label: '🚻 Wyjście do toalety', tone: 'primary' },
  CHECK_OUT: { label: '⏹️ Zakończ pracę', tone: 'danger' },
};

const formatMinutes = (minutes) => {
  if (minutes === null || minutes === undefined) return '—';
  const hrs = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hrs === 0) return `${mins} min`;
  return `${hrs} h ${mins} min`;
};

const minutesSince = (iso) => {
  if (!iso) return null;
  const diffMs = Date.now() - new Date(iso).getTime();
  if (Number.isNaN(diffMs)) return null;
  return Math.max(0, Math.floor(diffMs / 60000));
};

const getConfigValue = (key, fallback) => {
  const globalConfig = window?.APP_CONFIG || window?.TABLET_CONFIG || window?.ENV || window?.env;
  if (globalConfig && globalConfig[key] !== undefined && globalConfig[key] !== null) {
    return globalConfig[key];
  }
  const metaValue = document.querySelector(`meta[name="${key}"]`)?.content;
  if (metaValue) return metaValue;
  return fallback;
};

const useDeviceSettings = () => {
  const deviceToken = ref(getConfigValue('deviceToken', ''));
  const deviceId = ref(getConfigValue('deviceId', 'tablet-01'));

  return { deviceToken, deviceId };
};

const buildHeaders = (token, extra = {}) => {
  const headers = { ...extra };
  const tokenValue = (token || '').trim();
  if (tokenValue) headers['X-Device-Token'] = tokenValue;
  return headers;
};

const loadQrLibrary = () => new Promise((resolve, reject) => {
  if (window.Html5Qrcode) {
    resolve(window.Html5Qrcode);
    return;
  }
  const script = document.createElement('script');
  script.src = QR_LIB_URL;
  script.onload = () => resolve(window.Html5Qrcode);
  script.onerror = () => reject(new Error('Nie udało się załadować biblioteki skanera.'));
  document.head.appendChild(script);
});

const StatusDetails = {
  name: 'StatusDetails',
  props: {
    status: { type: Object, required: true },
  },
  setup(props) {
    const workTime = computed(() => formatMinutes(props.status.work_minutes));
    const breakTime = computed(() => {
      if (props.status.minutes_on_break !== null && props.status.minutes_on_break !== undefined) {
        return `${formatMinutes(props.status.break_minutes)} (w trakcie: ${props.status.minutes_on_break} min)`;
      }
      return formatMinutes(props.status.break_minutes);
    });
    const toiletInfo = computed(() => {
      if (props.status.last_event_type !== 'TOILET') return 'Brak';
      const mins = minutesSince(props.status.last_event_timestamp);
      if (mins === null) return 'Brak danych';
      return `${mins} min temu`;
    });

    return { workTime, breakTime, toiletInfo };
  },
  template: `
    <div class="meta">
      <div><strong>Pracownik:</strong> {{ status.employee.name }}</div>
      <div><strong>Status:</strong> {{ status.state }}</div>
      <div><strong>Start dnia:</strong> {{ status.started_at || '—' }}</div>
      <div><strong>Czas pracy:</strong> {{ workTime }}</div>
      <div><strong>Przerwy:</strong> {{ breakTime }}</div>
      <div><strong>Ostatnia akcja:</strong> {{ status.last_action || '—' }}</div>
      <div><strong>Ostatnie zdarzenie:</strong> {{ status.last_event_timestamp ? new Date(status.last_event_timestamp).toLocaleTimeString() : '—' }}</div>
      <div><strong>Toaleta:</strong> {{ toiletInfo }}</div>
    </div>
  `,
};

const HomeView = {
  name: 'HomeView',
  template: `
    <div class="container fullscreen">
      <div class="hero">
        <h1>Rejestracja czasu pracy</h1>
        <p class="muted">Wybierz tryb tabletu. Dostępne są jedynie najważniejsze kafle.</p>
      </div>
      <div class="tile-grid">
        <router-link class="tile primary" to="/scan">
          <div class="tile-icon">▶</div>
          <div>
            <h2>Rejestracja</h2>
            <p class="muted">Skanowanie kodu QR i wysyłanie zdarzeń</p>
          </div>
        </router-link>
        <router-link class="tile" to="/status">
          <div class="tile-icon">📊</div>
          <div>
            <h2>Status</h2>
            <p class="muted">Podgląd bieżącego stanu pracownika</p>
          </div>
        </router-link>
      </div>
    </div>
  `,
};

const StatusView = {
  name: 'StatusView',
  components: { StatusDetails },
  setup() {
    const { deviceToken, deviceId } = useDeviceSettings();
    const route = useRoute();
    const qrInput = ref(route.query.qr || '');
    const status = ref(null);
    const loading = ref(false);
    const error = ref('');

    const fetchStatus = async () => {
      if (!qrInput.value) {
        error.value = 'Podaj token QR';
        return;
      }
      loading.value = true;
      error.value = '';
      try {
        const params = new URLSearchParams({ qr: qrInput.value });
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

    onMounted(() => {
      if (qrInput.value) fetchStatus();
    });

    return { deviceId, deviceToken, qrInput, status, loading, error, fetchStatus };
  },
  template: `
    <div class="container">
      <router-link class="back-link" to="/">← Powrót do startu</router-link>
      <div class="grid two">
        <div class="card">
          <h2>Status pracownika</h2>
          <label class="label" for="qr">Token QR</label>
          <input id="qr" v-model="qrInput" placeholder="Zeskanowany token" />
          <button class="primary" style="margin-top:12px" @click="fetchStatus" :disabled="loading">{{ loading ? 'Pobieranie...' : 'Pobierz status' }}</button>
          <p class="helper" style="margin-top:8px">Możesz wejść na tę stronę po skanowaniu, aby ponownie podejrzeć status.</p>
          <p v-if="error" class="alert">{{ error }}</p>
        </div>
        <div class="card" v-if="status">
          <h3>Podsumowanie</h3>
          <StatusDetails :status="status" />
          <p class="helper" style="margin-top:12px">Dostępne akcje: {{ status.actions.join(', ') }}</p>
        </div>
      </div>
    </div>
  `,
};

const ScanView = {
  name: 'ScanView',
  components: { StatusDetails },
  setup() {
    const { deviceToken, deviceId } = useDeviceSettings();
    const router = useRouter();
    const route = useRoute();
    const mode = computed(() => (route.query.mode === 'status' ? 'status' : 'register'));
    const isRegisterMode = computed(() => mode.value === 'register');

    const scanning = ref(true);
    const scannedQr = ref('');
    const manualQr = ref('');
    const status = ref(null);
    const statusError = ref('');
    const statusLoading = ref(false);
    const message = ref('');
    const countdown = ref(null);
    const scannerError = ref('');
    let html5QrcodeInstance = null;
    let returnTimer = null;
    let countdownTimer = null;

    const stopCountdown = () => {
      if (returnTimer) clearTimeout(returnTimer);
      if (countdownTimer) clearInterval(countdownTimer);
      countdown.value = null;
    };

    const startReturn = () => {
      stopCountdown();
      let seconds = 3;
      countdown.value = seconds;
      countdownTimer = setInterval(() => {
        seconds -= 1;
        countdown.value = seconds;
        if (seconds <= 0) {
          clearInterval(countdownTimer);
        }
      }, 1000);
      returnTimer = setTimeout(() => router.push('/'), seconds * 1000);
    };

    const stopScanner = () => {
      scanning.value = false;
      if (html5QrcodeInstance) {
        html5QrcodeInstance.stop().catch(() => {});
      }
    };

    const startScanner = async () => {
      try {
        const Html5Qrcode = await loadQrLibrary();
        const cameras = await Html5Qrcode.getCameras();
        if (!cameras.length) {
          scannerError.value = 'Brak dostępnej kamery';
          return;
        }
        html5QrcodeInstance = new Html5Qrcode('reader');
        await html5QrcodeInstance.start(
          cameras[0].id,
          { fps: 10, qrbox: 250 },
          (decodedText) => onScan(decodedText),
        );
        scanning.value = true;
      } catch (err) {
        scannerError.value = err.message || 'Nie udało się uruchomić skanera';
      }
    };

    const fetchStatus = async (qr, { autoRegister = false } = {}) => {
      statusLoading.value = true;
      statusError.value = '';
      message.value = '';
      try {
        const params = new URLSearchParams({ qr });
        if (deviceId.value) params.set('device', deviceId.value);
        const resp = await fetch(`${API_BASE}/status/?${params.toString()}`, {
          headers: buildHeaders(deviceToken.value),
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || data.message || 'Błąd statusu');
        status.value = data;
        const canAutoCheckIn = (
          autoRegister
          && Array.isArray(data.actions)
          && data.actions.length === 1
          && data.actions[0] === 'CHECK_IN'
        );
        if (canAutoCheckIn) {
          await sendEvent('CHECK_IN');
        }
      } catch (err) {
        status.value = null;
        statusError.value = err.message;
      } finally {
        statusLoading.value = false;
      }
    };

    const sendEvent = async (eventType) => {
      if (!scannedQr.value) return;
      statusLoading.value = true;
      message.value = '';
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
        message.value = data.message || 'Zapisano';
        startReturn();
      } catch (err) {
        statusError.value = err.message;
      } finally {
        statusLoading.value = false;
      }
    };

    const onScan = (decodedText) => {
      scannedQr.value = decodedText;
      manualQr.value = decodedText;
      status.value = null;
      statusError.value = '';
      message.value = '';
      stopScanner();
      stopCountdown();
      const autoRegister = isRegisterMode.value;
      fetchStatus(decodedText, { autoRegister });
    };

    const submitManual = () => {
      if (!manualQr.value) return;
      scannedQr.value = manualQr.value;
      status.value = null;
      statusError.value = '';
      message.value = '';
      stopScanner();
      stopCountdown();
      const autoRegister = isRegisterMode.value;
      fetchStatus(manualQr.value, { autoRegister });
    };

    onMounted(() => startScanner());
    onBeforeUnmount(() => {
      stopScanner();
      stopCountdown();
    });

    return {
      actionMeta,
      scannedQr,
      manualQr,
      status,
      statusError,
      statusLoading,
      message,
      countdown,
      scannerError,
      deviceId,
      deviceToken,
      mode,
      isRegisterMode,
      startScanner,
      submitManual,
      sendEvent,
    };
  },
  template: `
    <div class="container">
      <router-link class="back-link" to="/">← Powrót do startu</router-link>
      <div class="grid two">
        <div class="card">
          <h2>Skanuj kod QR</h2>
          <div class="badge info" style="margin-bottom:12px">
            Tryb: {{ isRegisterMode ? 'Rejestracja' : 'Status' }}
          </div>
          <div id="reader" class="scanner">
            <div class="hint" v-if="scannerError">{{ scannerError }}</div>
            <div class="hint" v-else>Oczekiwanie na kamerę…</div>
          </div>
          <div style="margin-top:12px">
            <label class="label">Token ręcznie</label>
            <input v-model="manualQr" placeholder="Wpisz token, jeśli kamera jest niedostępna" />
            <button class="primary" style="margin-top:8px" @click="submitManual">Użyj tokenu</button>
          </div>
        </div>
        <div class="card">
          <h3>Wynik skanowania</h3>
          <p class="muted" v-if="!scannedQr">Zeskanuj kod, aby zobaczyć dostępne akcje.</p>
          <div v-if="scannedQr">
            <div class="badge info">Token: {{ scannedQr }}</div>
            <p v-if="statusError" class="alert">{{ statusError }}</p>
            <p v-if="statusLoading">Ładowanie statusu…</p>
            <div v-if="status">
              <StatusDetails :status="status" v-if="mode === 'status' || status.actions.length > 1" />
              <p class="helper" v-if="isRegisterMode && status.actions.length === 1">Wykonano domyślną akcję CHECK_IN.</p>
              <div
                class="action-grid"
                style="margin-top:16px"
                v-if="mode === 'status' || status.actions.length > 1"
              >
                <button
                  v-for="action in status.actions"
                  :key="action"
                  class="btn"
                  :class="actionMeta[action]?.tone || 'primary'"
                  :disabled="statusLoading"
                  @click="sendEvent(action)"
                >
                  {{ actionMeta[action]?.label || action }}
                </button>
              </div>
              <div v-if="message" class="card" style="margin-top:12px; background:#f8fafc;">
                <h4>Potwierdzenie</h4>
                <p style="margin:0">{{ message }}</p>
                <p class="helper" v-if="countdown !== null" style="margin-top:6px">Powrót na ekran główny za {{ countdown }}s…</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
};

const router = createRouter({
  history: createWebHistory('/api/tablet/'),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/status', name: 'status', component: StatusView },
    { path: '/scan', name: 'scan', component: ScanView },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
});

const AppShell = {
  template: `
    <main class="app-shell">
      <router-view></router-view>
    </main>
  `,
};

const app = createApp(AppShell);
app.use(router);
app.mount('#app');
