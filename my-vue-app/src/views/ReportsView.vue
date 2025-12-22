<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const formatDateInput = (date) => date.toISOString().slice(0, 10)
const today = new Date()
const weekAgo = new Date()
weekAgo.setDate(today.getDate() - 6)

const filters = reactive({
  from: formatDateInput(weekAgo),
  to: formatDateInput(today),
  employeeId: '',
})

const report = ref(null)
const loading = ref(false)
const error = ref('')

const hasRange = computed(() => filters.from && filters.to)

const csvUrl = computed(() => {
  if (!hasRange.value) return null

  const params = new URLSearchParams({
    from: filters.from,
    to: filters.to,
  })

  if (filters.employeeId) {
    params.append('employee_id', filters.employeeId.trim())
  }

  return `/api/admin/reports/attendance.csv/?${params.toString()}`
})

const summaryTotals = computed(() => {
  if (!report.value?.employees?.length) return null

  return report.value.employees.reduce(
    (acc, curr) => {
      const totals = curr.totals || {}
      acc.planned += totals.planned_minutes || 0
      acc.worked += totals.worked_minutes || 0
      acc.late += totals.late_minutes || 0
      acc.anomalies += totals.anomaly_days || 0
      return acc
    },
    { planned: 0, worked: 0, late: 0, anomalies: 0 }
  )
})

const formatMinutes = (minutes) => {
  if (minutes === undefined || minutes === null || Number.isNaN(Number(minutes))) return '—'
  const total = Math.max(0, Number(minutes))
  const hours = Math.floor(total / 60)
  const mins = Math.floor(total % 60)
  return `${hours} h ${mins.toString().padStart(2, '0')} min`
}

const fetchReport = async () => {
  if (!hasRange.value) {
    error.value = 'Podaj zakres dat (od/do).'
    return
  }

  loading.value = true
  error.value = ''

  const params = new URLSearchParams({
    from: filters.from,
    to: filters.to,
  })

  if (filters.employeeId) {
    params.append('employee_id', filters.employeeId.trim())
  }

  try {
    const response = await fetch(`/api/admin/reports/attendance/?${params.toString()}`)

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || 'Nie udało się pobrać raportu')
    }

    report.value = await response.json()
  } catch (err) {
    error.value = err?.message || 'Błąd pobierania raportu'
  } finally {
    loading.value = false
  }
}

onMounted(fetchReport)
</script>

<template>
  <section class="panel">
    <div class="panel__header">
      <div>
        <p class="eyebrow">Raporty</p>
        <h1>Raport obecności</h1>
        <p class="muted">Przegląd zdarzeń z podsumowaniem planu, pracy i anomalii.</p>
      </div>
      <div class="actions actions--no-margin">
        <a
          v-if="csvUrl"
          class="btn"
          :href="csvUrl"
          target="_blank"
          rel="noopener noreferrer"
          :aria-disabled="loading"
          >Pobierz CSV</a
        >
        <button class="btn btn--primary" type="button" :disabled="loading" @click="fetchReport">
          {{ loading ? 'Ładowanie…' : 'Odśwież' }}
        </button>
      </div>
    </div>

    <div class="filters">
      <label class="field">
        <span>Od</span>
        <input v-model="filters.from" type="date" />
      </label>
      <label class="field">
        <span>Do</span>
        <input v-model="filters.to" type="date" />
      </label>
      <label class="field">
        <span>ID pracownika (opcjonalnie)</span>
        <input v-model="filters.employeeId" type="number" min="1" placeholder="np. 5" />
      </label>
    </div>

    <div v-if="error" class="alert alert--error">{{ error }}</div>

    <template v-if="report">
      <div class="chips" aria-hidden="true">
        <span class="chip">Zakres: {{ report.range?.from }} → {{ report.range?.to }}</span>
        <span class="chip">Próg spóźnienia: {{ report.late_threshold_minutes }} min</span>
      </div>

      <div v-if="summaryTotals" class="stats-grid">
        <div class="stat">
          <p class="eyebrow">Planowane</p>
          <p class="stat__value">{{ formatMinutes(summaryTotals.planned) }}</p>
          <p class="muted">Łączny czas w grafiku</p>
        </div>
        <div class="stat">
          <p class="eyebrow">Przepracowane</p>
          <p class="stat__value">{{ formatMinutes(summaryTotals.worked) }}</p>
          <p class="muted">Czas po odjęciu przerw</p>
        </div>
        <div class="stat">
          <p class="eyebrow">Spóźnienia</p>
          <p class="stat__value">{{ summaryTotals.late }} min</p>
          <p class="muted">Łączne minuty spóźnień</p>
        </div>
        <div class="stat">
          <p class="eyebrow">Anomalie</p>
          <p class="stat__value">{{ summaryTotals.anomalies }}</p>
          <p class="muted">Dni z nieprawidłowymi zdarzeniami</p>
        </div>
      </div>

      <div v-if="report.employees?.length" class="table-wrapper">
        <table class="table">
          <thead>
            <tr>
              <th>Pracownik</th>
              <th>Planowane</th>
              <th>Przepracowane</th>
              <th>Spóźnienia</th>
              <th>Anomalie</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in report.employees" :key="row.employee.id">
              <td>{{ row.employee.name }}</td>
              <td class="mono">{{ formatMinutes(row.totals.planned_minutes) }}</td>
              <td class="mono">{{ formatMinutes(row.totals.worked_minutes) }}</td>
              <td class="mono">{{ row.totals.late_minutes }} min</td>
              <td class="mono">{{ row.totals.anomaly_days }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="muted">Brak danych dla wybranego filtra.</p>
    </template>
    <p v-else-if="!loading && !error" class="muted">Użyj filtrów, aby wygenerować raport.</p>
  </section>
</template>
