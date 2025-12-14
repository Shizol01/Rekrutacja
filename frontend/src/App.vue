<script setup>
import {ref, onMounted} from "vue"

const schedules = ref([])
const report = ref(null)
const loading = ref(false)
const error = ref(null)

const from = ref("2025-12-01")
const to = ref("2026-01-31")

async function fetchData() {
  loading.value = true
  error.value = null

  try {
    const [schedulesResp, reportResp] = await Promise.all([
      fetch(`http://localhost:8000/api/admin/schedules/?from=${from.value}&to=${to.value}`),
      fetch(`http://localhost:8000/api/admin/reports/attendance/?from=${from.value}&to=${to.value}`)
    ])

    schedules.value = await schedulesResp.json()
    report.value = await reportResp.json()
  } catch (e) {
    error.value = "Nie udało się pobrać danych"
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

function dayTypeLabel(type) {
  return {
    WORK: "Roboczy",
    OFF: "Wolne",
    LEAVE: "Urlop",
    NO_SCHEDULE: "Brak grafiku",
  }[type] || type
}
</script>

<template>
  <main class="container">
    <h1>⏱️ Rejestracja czasu pracy</h1>

    <!-- FILTER -->
    <section class="card">
      <h2>Zakres dat</h2>
      <div class="filters">
        <label>
          Od:
          <input type="date" v-model="from"/>
        </label>
        <label>
          Do:
          <input type="date" v-model="to"/>
        </label>
        <button @click="fetchData">Odśwież</button>
      </div>
    </section>

    <p v-if="loading" class="info">Ładowanie danych…</p>
    <p v-if="error" class="error">{{ error }}</p>

    <!-- GRAFIK -->
    <section v-if="schedules.length" class="card">
      <h2>📅 Grafik pracy</h2>
      <table>
        <thead>
        <tr>
          <th>Pracownik</th>
          <th>Data</th>
          <th>Typ dnia</th>
          <th>Start</th>
          <th>Koniec</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="s in schedules" :key="s.id">
          <td>{{ s.employee }}</td>
          <td>{{ s.date }}</td>
          <td>
            <span :class="['badge', s.day_type.toLowerCase()]">
              {{ dayTypeLabel(s.day_type) }}
            </span>
          </td>
          <td>{{ s.planned_start || "-" }}</td>
          <td>{{ s.planned_end || "-" }}</td>
        </tr>
        </tbody>
      </table>
    </section>

    <!-- RAPORT -->
    <section v-if="report" class="card">
      <h2>📊 Raport czasu pracy</h2>

      <div v-for="emp in report.employees" :key="emp.employee.id" class="employee-block">
        <h3>{{ emp.employee.name }}</h3>

        <table>
          <thead>
          <tr>
            <th>Data</th>
            <th>Typ dnia</th>
            <th>Plan (min)</th>
            <th>Praca (min)</th>
            <th>Przerwy (min)</th>
            <th>Spóźnienie</th>
            <th>Absencja</th>
            <th>Anomalie</th>
          </tr>
          </thead>
          <tbody>
          <tr v-for="day in emp.days" :key="day.date">
            <td>{{ day.date }}</td>
            <td>{{ dayTypeLabel(day.day_type) }}</td>

            <td>{{ day.planned.minutes }}</td>

            <td>{{ day.actual.worked_minutes }}</td>

            <!-- PRZERWY -->
            <td>{{ day.actual.break_minutes }}</td>

            <!-- SPÓŹNIENIE -->
            <td>
    <span v-if="day.lateness_minutes > 0" style="color:#b91c1c">
      ⏰ {{ day.lateness_minutes }} min
    </span>
              <span v-else>—</span>
            </td>

            <!-- ABSENCJA -->
            <td>{{ day.absence ? "TAK" : "NIE" }}</td>

            <!-- ANOMALIE -->
            <td>
              <ul v-if="day.anomalies.length">
                <li v-for="a in day.anomalies" :key="a.type">
                  {{ a.type }}
                </li>
              </ul>
              <span v-else>—</span>
            </td>
          </tr>

          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style>
.container {
  max-width: 1100px;
  margin: auto;
  padding: 20px;
  font-family: system-ui, sans-serif;
}

h1 {
  margin-bottom: 20px;
}

.card {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, .08);
}

.filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

button {
  padding: 6px 12px;
  cursor: pointer;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 8px;
  border-bottom: 1px solid #ddd;
  text-align: left;
}

thead {
  background: #f5f5f5;
}

.employee-block {
  margin-top: 20px;
}

.badge {
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 0.85em;
}

.badge.work {
  background: #d1fae5;
  color: #065f46;
}

.badge.off {
  background: #e5e7eb;
}

.badge.leave {
  background: #fde68a;
}

.info {
  color: #555;
}

.error {
  color: #b91c1c;
  font-weight: bold;
}
</style>
