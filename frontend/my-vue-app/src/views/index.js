import {
  computed,
  onBeforeUnmount,
  onMounted,
  ref,
} from 'vue';
import { useRoute, useRouter } from 'vue-router';

const API_BASE = import.meta.env.VITE_API_BASE || '/api/tablet';
const QR_LIB_URL = 'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js';

const actionMeta = {
  CHECK_IN: { label: '▶ Rozpocznij pracę', tone: 'success' },
  BREAK_START: { label: '☕ Rozpocznij przerwę', tone: 'warning' },
  BREAK_END: { label: '▶ Zakończ przerwę', tone: 'success' },
  TOILET: { label: '🚻 Wyjście do toalety', tone: 'primary' },
  CHECK_OUT: { label: '⏹️ Zakończ pracę', tone: 'danger' },
};

const actionBadges = {
  CHECK_IN: 'Wejście',
  BREAK_START: 'Przerwa',
  BREAK_END: 'Koniec przerwy',
  TOILET: 'Toaleta',
  CHECK_OUT: 'Wyjście',
};

const stateMeta = {
  WORKING: { label: 'Jesteś w pracy', tone: 'success' },
  ON_BREAK: { label: 'Przerwa', tone: 'warning' },
  OFF_DUTY: { label: 'Poza pracą', tone: 'danger' },
};

const formatMinutes = (minutes) => {
  if (minutes === null || minutes === undefined) return '—';
  const hrs = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hrs === 0) return `${mins} min`;
  return `${hrs} h ${mins} min`;
};

const formatClock = (iso) => {
  if (!iso) return '—';
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return '—';
  return dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const deviceId = (window.APP_CONFIG?.deviceId || import.meta.env.VITE_DEVICE_ID || 'tablet-01');
const deviceToken = (
  window.APP_CONFIG?.deviceToken
  || import.meta.env.VITE_DEVICE_TOKEN
  || ''
).trim();

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

const createAutoClose = () => {
  const countdown = ref(null);
  let countdownEndsAt = null;
  let countdownTimer = null;
  let onFinish = null;

  const stop = () => {
    if (countdownTimer) clearInterval(countdownTimer);
    countdownTimer = null;
    countdownEndsAt = null;
    onFinish = null;
    countdown.value = null;
  };

  const finish = () => {
    const cb = onFinish;
    stop();
    if (cb) cb();
  };

  const start = (seconds, cb) => {
    stop();
    countdownEndsAt = Date.now() + seconds * 1000;
    onFinish = cb;
    countdown.value = seconds;
    countdownTimer = setInterval(() => {
      if (!countdownEndsAt) return;
      const remaining = Math.max(0, Math.ceil((countdownEndsAt - Date.now()) / 1000));
      countdown.value = remaining;
      if (remaining <= 0) {
        finish();
      }
    }, 500);
  };

  const extend = (extraSeconds = 60) => {
    if (!countdownEndsAt) return;
    countdownEndsAt += extraSeconds * 1000;
    countdown.value = Math.max(0, Math.ceil((countdownEndsAt - Date.now()) / 1000));
  };

  return { countdown, start, stop, extend, finish };
};

const StatusDetails = {
  name: 'StatusDetails',
  props: {
    status: { type: Object, required: true },
  },
  setup(props) {
    const workTime = computed(() => formatMinutes(props.status.work_minutes));
    const breakTime = computed(() => formatMinutes(props.status.break_minutes));
    const eventClock = computed(() => formatClock(props.status.last_event_timestamp));
    const email = computed(() => props.status.employee.email || props.status.employee.mail || '—');
    const available = computed(() => (props.status.actions || []).map((a) => actionBadges[a] || a));
    const state = computed(() => stateMeta[props.status.state] || { label: props.status.state, tone: 'info' });
    const isBreakActive = computed(
      () => props.status.minutes_on_break !== null && props.status.minutes_on_break !== undefined,
    );
    const lastEventLabel = computed(
      () => actionBadges[props.status.last_event_type] || props.status.last_action || '—',
    );

    return {
      workTime,
      breakTime,
      eventClock,
      email,
      available,
      state,
      isBreakActive,
      lastEventLabel,
    };
  },
  template: `
    <div class="status-details">
      <div class="status-header">
        <div>
          <p class="eyebrow">Pracownik</p>
          <h3 style="margin: 4px 0">{{ status.employee.name }}</h3>
          <p class="muted">{{ email }}</p>
        </div>
        <span class="badge" :class="state.tone">{{ state.label }}</span>
      </div>

      <div class="quick-grid">
        <div class="quick-card">
          <p class="helper">Czas pracy</p>
          <div class="stat-value">{{ workTime }}</div>
        </div>
        <div class="quick-card">
          <p class="helper">Przerwy</p>
          <div class="stat-value">{{ breakTime }}</div>
          <p class="helper" v-if="isBreakActive">Aktywna: {{ status.minutes_on_break }} min</p>
          <p class="helper" v-else>Brak aktywnej przerwy</p>
        </div>
        <div class="quick-card">
          <p class="helper">Przyjście</p>
          <div class="stat-value">{{ status.started_at || '—' }}</div>
        </div>
        <div class="quick-card">
          <p class="helper">Ostatnie zdarzenie</p>
          <div class="stat-value">{{ eventClock }}</div>
          <div class="pill-row" v-if="lastEventLabel && lastEventLabel !== '—'">
            <span class="pill info">{{ lastEventLabel }}</span>
          </div>
          <p class="helper">{{ status.last_action || '—' }}</p>
        </div>
      </div>

      <div class="meta-row">
        <div>
          <p class="helper" style="margin-bottom:6px">Dostępne akcje</p>
          <div class="pill-row">
            <span class="pill" v-for="action in available" :key="action">{{ action }}</span>
          </div>
        </div>
        <div v-if="status.minutes_on_break !== null" class="pill warning">Czas przerwy: {{ status.minutes_on_break }} min</div>
      </div>
    </div>
  `,
};

const ConfirmationCard = {
  name: 'ConfirmationCard',
  props: {
    status: { type: Object, required: true },
    countdown: { type: Number, default: null },
    message: { type: String, default: '' },
  },
  emits: ['close', 'extend'],
  setup(props) {
    const shortcutItems = computed(() => [
      ...(props.status.minutes_on_break !== null && props.status.minutes_on_break !== undefined
        ? [{ label: 'Aktywna przerwa', value: `${props.status.minutes_on_break} min` }]
        : []),
      { label: 'Czas pracy', value: formatMinutes(props.status.work_minutes) },
      { label: 'Przerwy', value: formatMinutes(props.status.break_minutes) },
      { label: 'Przyjście', value: props.status.started_at || '—' },
      { label: 'Ostatnie zdarzenie', value: formatClock(props.status.last_event_timestamp) },
    ]);
    const title = computed(() => props.message || props.status.last_action || 'Ostatnie zdarzenie');
    const breakInfo = computed(() => (
      props.status.minutes_on_break !== null && props.status.minutes_on_break !== undefined
        ? `${props.status.minutes_on_break} min`
        : null
    ));
    const actionLabel = computed(
      () => actionBadges[props.status.last_event_type] || props.status.last_action || 'Zdarzenie',
    );
    const actionTone = computed(() => actionMeta[props.status.last_event_type]?.tone || 'info');

    return {
      shortcutItems, title, breakInfo, formatClock, actionLabel, actionTone,
    };
  },
  template: `
    <div class="card confirmation-card">
      <div class="confirmation-head">
        <div>
          <p class="eyebrow">Potwierdzenie</p>
          <div class="confirmation-meta">
            <span class="badge" :class="actionTone">{{ actionLabel }}</span>
            <span class="muted">o {{ formatClock(status.last_event_timestamp) }}</span>
          </div>
          <h4 style="margin: 6px 0">{{ title }}</h4>
        </div>
        <div v-if="breakInfo" class="pill warning">Przerwa trwa: {{ breakInfo }}</div>
      </div>

      <div class="shortcut-grid">
        <div class="shortcut" v-for="item in shortcutItems" :key="item.label">
          <p class="helper">{{ item.label }}</p>
          <div class="stat-value">{{ item.value }}</div>
        </div>
      </div>

      <div class="confirmation-actions">
        <button class="btn primary" type="button" @click="$emit('close')">
          Zamknij<span v-if="countdown !== null"> ({{ countdown }}s)</span>
        </button>
        <button class="btn ghost" type="button" :disabled="countdown === null" @click="$emit('extend')">+60s</button>
      </div>
    </div>
  `,
};

const HomeView = {
  name: 'HomeView',
  template: `
    <div class="fullscreen-wrapper">
      <div class="home-content">
        <div class="tile-grid home-tiles">
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
    </div>
  `,
};

const StatusView = {
  name: 'StatusView',
  components: { StatusDetails, ConfirmationCard },
  setup() {
    const router = useRouter();
    const route = useRoute();
    const qrInput = ref(route.query.qr || '');
    const status = ref(null);
    const loading = ref(false);
    const actionLoading = ref(false);
    const error = ref('');
    const message = ref('');
    const showConfirmation = ref(false);
    const { countdown, start, stop, extend, finish } = createAutoClose();

    const startReturn = () => {
      start(4, () => router.push('/'));
    };

    const handleClose = () => {
      if (countdown.value !== null) {
        finish();
      } else {
        stop();
        showConfirmation.value = false;
      }
    };

    const fetchStatus = async ({ preserveMessage = false } = {}) => {
      if (!qrInput.value) {
        error.value = 'Podaj token QR';
        return;
      }
      loading.value = true;
      error.value = '';
      if (!preserveMessage) message.value = '';
      stop();
      try {
        const params = new URLSearchParams({ qr: qrInput.value });
        if (deviceId) params.set('device', deviceId);
        const resp = await fetch(`${API_BASE}/status/?${params.toString()}`, {
          headers: buildHeaders(deviceToken),
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || data.message || 'Błąd statusu');
        status.value = data;
        showConfirmation.value = true;
      } catch (err) {
        status.value = null;
        showConfirmation.value = false;
        stop();
        error.value = err.message;
      } finally {
        loading.value = false;
      }
    };

    onMounted(() => {
      if (qrInput.value) fetchStatus();
    });

    onBeforeUnmount(() => stop());

    const sendEvent = async (eventType) => {
      if (!qrInput.value) {
        error.value = 'Podaj token QR przed wysłaniem akcji';
        return;
      }
      actionLoading.value = true;
      error.value = '';
      try {
        const resp = await fetch(`${API_BASE}/events/`, {
          method: 'POST',
          headers: buildHeaders(deviceToken, { 'Content-Type': 'application/json' }),
          body: JSON.stringify({
            qr: qrInput.value,
            event_type: eventType,
            device_id: deviceId || undefined,
          }),
        });
        const data = await resp.json();
        if (!resp.ok && resp.status !== 200 && resp.status !== 201) {
          throw new Error(data.detail || data.message || 'Błąd zapisu');
        }
        message.value = data.message || 'Zapisano';
        await fetchStatus({ preserveMessage: true });
        startReturn();
      } catch (err) {
        error.value = err.message;
      } finally {
        actionLoading.value = false;
      }
    };

    const availableActions = computed(() => (status.value?.actions || []));
    const hasActions = computed(() => availableActions.value.length > 0);

    return {
      actionMeta,
      qrInput,
      status,
      loading,
      actionLoading,
      error,
      fetchStatus,
      showConfirmation,
      countdown,
      message,
      extend,
      finish,
      handleClose,
      sendEvent,
      availableActions,
      hasActions,
    };
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
          <div
            class="action-grid"
            style="margin-top:16px"
            v-if="hasActions"
          >
            <button
              v-for="action in availableActions"
              :key="action"
              class="btn"
              :class="actionMeta[action]?.tone || 'primary'"
              :disabled="loading || actionLoading"
              @click="sendEvent(action)"
            >
              {{ actionMeta[action]?.label || action }}
            </button>
          </div>
          <ConfirmationCard
            v-if="showConfirmation"
            :status="status"
            :countdown="countdown"
            :message="message || status.last_action"
            @close="handleClose"
            @extend="extend"
          />
        </div>
      </div>
    </div>
  `,
};

const ScanView = {
  name: 'ScanView',
  components: { StatusDetails, ConfirmationCard },
  setup() {
    const router = useRouter();
    const route = useRoute();
    const mode = computed(() => (route.query.mode === 'status' ? 'status' : 'register'));
    const isRegisterMode = computed(() => mode.value === 'register');

    const scanning = ref(true);
    const scannedQr = ref('');
    const status = ref(null);
    const statusError = ref('');
    const statusLoading = ref(false);
    const message = ref('');
    const showConfirmation = ref(false);
    const { countdown, start, stop, extend, finish } = createAutoClose();
    const scannerError = ref('');
    const autoCheckInTriggered = ref(false);
    let html5QrcodeInstance = null;

    const startReturn = () => {
      start(3, () => router.push('/'));
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

    const fetchStatus = async (
      qr,
      { autoRegister = false, preserveMessage = false, preserveAutoFlag = false } = {},
    ) => {
      statusLoading.value = true;
      statusError.value = '';
      if (!preserveMessage) message.value = '';
      if (!preserveAutoFlag) autoCheckInTriggered.value = false;
      stop();
      try {
        const params = new URLSearchParams({ qr });
        if (deviceId) params.set('device', deviceId);
        const resp = await fetch(`${API_BASE}/status/?${params.toString()}`, {
          headers: buildHeaders(deviceToken),
        });
        const data = await resp.json();
        if (!resp.ok) throw new Error(data.detail || data.message || 'Błąd statusu');
        status.value = data;
        showConfirmation.value = true;
        const canAutoCheckIn = (
          autoRegister
          && Array.isArray(data.actions)
          && data.actions.length === 1
          && data.actions[0] === 'CHECK_IN'
        );
        if (canAutoCheckIn) {
          autoCheckInTriggered.value = true;
          await sendEvent('CHECK_IN', { preserveAutoFlag: true });
        }
      } catch (err) {
        status.value = null;
        showConfirmation.value = false;
        statusError.value = err.message;
      } finally {
        statusLoading.value = false;
      }
    };

    const sendEvent = async (eventType, { preserveAutoFlag = false } = {}) => {
      if (!scannedQr.value) return;
      statusLoading.value = true;
      message.value = '';
      try {
        const resp = await fetch(`${API_BASE}/events/`, {
          method: 'POST',
          headers: buildHeaders(deviceToken, { 'Content-Type': 'application/json' }),
          body: JSON.stringify({
            qr: scannedQr.value,
            event_type: eventType,
            device_id: deviceId || undefined,
          }),
        });
        const data = await resp.json();
        if (!resp.ok && resp.status !== 200 && resp.status !== 201) {
          throw new Error(data.detail || data.message || 'Błąd zapisu');
        }
        message.value = data.message || 'Zapisano';
        await fetchStatus(scannedQr.value, {
          autoRegister: false,
          preserveMessage: true,
          preserveAutoFlag,
        });
        startReturn();
      } catch (err) {
        statusError.value = err.message;
        autoCheckInTriggered.value = false;
      } finally {
        statusLoading.value = false;
      }
    };

    const onScan = (decodedText) => {
      scannedQr.value = decodedText;
      status.value = null;
      statusError.value = '';
      message.value = '';
      autoCheckInTriggered.value = false;
      stopScanner();
      stop();
      showConfirmation.value = false;
      const autoRegister = isRegisterMode.value;
      fetchStatus(decodedText, { autoRegister });
    };

    onMounted(() => startScanner());
    onBeforeUnmount(() => {
      stopScanner();
      stop();
    });

    const shouldShowActionButtons = computed(() => {
      if (!status.value || !Array.isArray(status.value.actions)) return false;
      if (autoCheckInTriggered.value) return false;
      if (mode.value === 'status') return status.value.actions.length > 0;
      if (status.value.actions.length === 1 && status.value.actions[0] === 'CHECK_IN') return false;
      return status.value.actions.length > 0;
    });

    return {
      actionMeta,
      scannedQr,
      status,
      statusError,
      statusLoading,
      message,
      countdown,
      showConfirmation,
      scannerError,
      autoCheckInTriggered,
      shouldShowActionButtons,
      mode,
      isRegisterMode,
      startScanner,
      sendEvent,
      extend,
      finish,
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
        </div>
        <div class="card">
          <h3>Wynik skanowania</h3>
          <p class="muted" v-if="!scannedQr">Zeskanuj kod, aby zobaczyć dostępne akcje.</p>
          <div v-if="scannedQr">
            <div class="badge info">Token: {{ scannedQr }}</div>
            <p v-if="statusError" class="alert">{{ statusError }}</p>
            <p v-if="statusLoading">Ładowanie statusu…</p>
            <div v-if="status">
              <StatusDetails :status="status" />
              <p class="helper" v-if="autoCheckInTriggered">Wykonano domyślną akcję CHECK_IN.</p>
              <div
                class="action-grid"
                style="margin-top:16px"
                v-if="shouldShowActionButtons"
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
              <ConfirmationCard
                v-if="showConfirmation"
                :status="status"
                :countdown="countdown"
                :message="message || status.last_action"
                @close="finish"
                @extend="extend"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
};

export {
  HomeView,
  ScanView,
  StatusView,
};
