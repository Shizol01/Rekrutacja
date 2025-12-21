<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { computed } from 'vue'

import { useDeviceSettings } from './composables/useDeviceSettings'

const { deviceToken, deviceId } = useDeviceSettings()

const tokenState = computed(() =>
  deviceToken.value ? 'Token urządzenia zapisany' : 'Brak zapisanego tokenu'
)
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand__dot" aria-hidden="true"></span>
        Tablet Console
      </div>
      <nav class="nav">
        <RouterLink to="/">Start</RouterLink>
        <RouterLink to="/scan">Skanuj</RouterLink>
        <RouterLink to="/status">Status</RouterLink>
        <RouterLink to="/schedule">Harmonogram</RouterLink>
        <RouterLink to="/reports">Raporty</RouterLink>
      </nav>
      <div class="topbar__status" :title="`Device ID: ${deviceId || '—'}`">
        {{ tokenState }}
      </div>
    </header>

    <main class="content">
      <RouterView />
    </main>
  </div>
</template>
