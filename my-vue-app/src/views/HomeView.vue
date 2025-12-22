<script setup>
import { useDeviceSettings } from '../composables/useDeviceSettings';

const { deviceToken, deviceId } = useDeviceSettings();
</script>

<template>
  <div class="grid two">
    <div class="card">
      <h2>Wybierz opcję</h2>
      <div class="grid three">
        <RouterLink class="tile green" to="/scan?mode=register">
          <div>Rejestracja</div>
          <div class="small">Skanuj kod i zapisz wejście/wyjście</div>
        </RouterLink>
        <RouterLink class="tile blue" to="/scan?mode=status">
          <div>Status</div>
          <div class="small">Podejrzyj bieżący stan po skanie</div>
        </RouterLink>
        <div class="tile orange disabled">
          <div>Urlopy</div>
          <div class="small">Wkrótce dostępne</div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3>Ustawienia urządzenia</h3>
      <p class="muted">Nagłówek <code>X-Device-Token</code> jest wymagany przez API. Id urządzenia trafia do logu zdarzeń.</p>
      <label class="label" for="token">Device token</label>
      <input id="token" class="input" v-model="deviceToken" placeholder="Wklej token urządzenia" autocomplete="off" />
      <label class="label" for="device" style="margin-top:12px">Id urządzenia</label>
      <input id="device" class="input" v-model="deviceId" placeholder="np. tablet-01" />
    </div>
  </div>
</template>
