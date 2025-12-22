<script setup>
import { onMounted, reactive, ref } from 'vue'

const formatDateInput = (date) => date.toISOString().slice(0, 10)
const today = new Date()
const weekAgo = new Date()
weekAgo.setDate(today.getDate() - 6)

const filters = reactive({
  from: formatDateInput(weekAgo),
  to: formatDateInput(today),
  employeeId: '',
})

const schedules = ref([])
const loading = ref(false)
const error = ref('')

const dayTypeLabel = {
  WORK: 'Praca',
  OFF: 'Wolne',
  LEAVE: 'Urlop',
}

const formatTime = (value) => (value ? value.slice(0, 5) : '—')

const fetchSchedules = async () => {
  if (!filters.from || !filters.to) {
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
    const response = await fetch(`/api/admin/schedules/?${params.toString()}`)

    if (!response.ok) {
      const text = await response.text()
      throw new Error(text || 'Nie udało się pobrać harmonogramu')
    }

    schedules.value = await response.json()
  } catch (err) {
    error.value = err?.message || 'Błąd pobierania danych'
  } finally {
    loading.value = false
  }
}

onMounted(fetchSchedules)
</script>

<template>
  <section class="panel">
    <div class="panel__header">
      <div>
        <p class="eyebrow">Harmonogram</p>
        <h1>Planowane zadania</h1>
        <p class="muted">Sprawdź grafik według zakresu dat i opcjonalnego pracownika.</p>
      </div>
      <button class="btn btn--primary" type="button" :disabled="loading" @click="fetchSchedules">
        {{ loading ? 'Ładowanie…' : 'Odśwież' }}
      </button>
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
        <input v-model="filters.employeeId" type="number" min="1" placeholder="np. 3" />
      </label>
    </div>

    <div v-if="error" class="alert alert--error">{{ error }}</div>

    <div v-if="schedules.length" class="table-wrapper">
      <table class="table">
        <thead>
          <tr>
            <th>Data</th>
            <th>Pracownik</th>
            <th>Typ dnia</th>
            <th>Start</th>
            <th>Koniec</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in schedules" :key="item.id">
            <td class="mono">{{ item.date }}</td>
            <td>{{ item.employee_name }}</td>
            <td>
              <span class="badge" :data-type="item.day_type">{{ dayTypeLabel[item.day_type] || item.day_type }}</span>
            </td>
            <td class="mono">{{ formatTime(item.planned_start) }}</td>
            <td class="mono">{{ formatTime(item.planned_end) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-else-if="!loading && !error" class="muted">Brak pozycji do wyświetlenia w wybranym zakresie.</p>
  </section>
</template>
