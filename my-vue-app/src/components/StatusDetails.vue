<script setup>
import { computed } from 'vue';
import { formatMinutes, humanTime } from '../utils/time';

const props = defineProps({
  status: {
    type: Object,
    required: true,
  },
});

const statusLabel = computed(() => {
  if (props.status.state === 'WORKING') return { text: 'Jesteś w pracy', tone: 'green' };
  if (props.status.state === 'ON_BREAK') return { text: 'Na przerwie', tone: 'orange' };
  return { text: 'Poza pracą', tone: 'gray' };
});
</script>

<template>
  <div class="card">
    <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
      <div style="width:42px; height:42px; border-radius:50%; background:#e0f2fe; color:#0c4a6e; display:flex; align-items:center; justify-content:center; font-weight:700;">
        {{ status.employee.name?.slice(0, 1) || 'P' }}
      </div>
      <div>
        <div style="font-weight:700;">{{ status.employee.name }}</div>
        <div class="small">Ostatnia akcja: {{ status.last_action || '—' }}</div>
      </div>
      <span class="badge" :class="statusLabel.tone" style="margin-left:auto;">{{ statusLabel.text }}</span>
    </div>

    <div class="status-grid" style="margin-top:14px;">
      <div class="status-box">
        <div class="small muted">Czas pracy</div>
        <div style="font-weight:700;">{{ formatMinutes(status.work_minutes) }}</div>
      </div>
      <div class="status-box">
        <div class="small muted">Przerwy</div>
        <div style="font-weight:700;">{{ formatMinutes(status.break_minutes) }}</div>
        <div class="small muted" v-if="status.minutes_on_break">w trakcie: {{ status.minutes_on_break }} min</div>
      </div>
      <div class="status-box">
        <div class="small muted">Przyjście</div>
        <div style="font-weight:700;">{{ status.started_at || '—' }}</div>
      </div>
      <div class="status-box">
        <div class="small muted">Ostatnie zdarzenie</div>
        <div style="font-weight:700;">{{ humanTime(status.last_event_timestamp) }}</div>
      </div>
    </div>
  </div>
</template>
