<template>
  <div class="calendar-wrapper">
    <div class="calendar-header">
      <button @click="goToPreviousMonth" class="arrow-button">⟨</button>
      <h3 class="calendar-title">{{ monthNames[currentMonth - 1] }} {{ currentYear }}</h3>
      <button @click="goToNextMonth" class="arrow-button">⟩</button>
    </div>

    <div class="toggle-buttons" v-if="dependents.length > 0">
      <button
        v-for="dep in dependents"
        :key="dep.id"
        @click="selectDependent(dep.id)"
        :class="{ active: selectedDependent === dep.id }"
      >
        {{ dep.name }}
      </button>
    </div>

    <div class="weekday-row">
      <div v-for="day in daysOfWeek" :key="day" class="weekday">{{ day }}</div>
    </div>

    <div class="calendar-grid">
      <div
        v-for="(day, index) in calendarData"
        :key="index"
        :class="['calendar-cell', {
          today: day.medicationData?.isToday,
          future: day.medicationData?.isFuture,
          past: day.medicationData?.isPast
        }]"
        :title="day.medicationData ? `Taken: ${day.medicationData.taken}\nMissed: ${day.medicationData.missed}` : ''"
      >
        <div class="cell-label">{{ day.label }}</div>
        <div class="cell-data">
          <template v-if="day.medicationData">
            <div class="status-bar-container">
              <div
                class="status-bar taken"
                :style="{ width: day.medicationData.takenPercentage + '%' }"
              ></div>
              <div
                class="status-bar missed"
                :style="{ width: day.medicationData.missedPercentage + '%' }"
              ></div>
            </div>
            <div class="total-meds">
              {{ (day.medicationData.taken || 0) + (day.medicationData.missed || 0) }} total
            </div>
          </template>
          <template v-else>
            <span class="future-placeholder">-</span>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import medicationService from '@/services/calendar.js';
import apiService from '@/services/apiService.js';

const currentDate = new Date();
const currentMonth = ref(currentDate.getMonth() + 1);
const currentYear = ref(currentDate.getFullYear());
const selectedDependent = ref(null);
const calendarData = ref([]);
const dependents = ref([]);

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

async function loadDependents() {
  try {
    const response = await apiService.get('/sc/my-dependents');
    dependents.value = response.data.dependents.map(dep => ({
      id: dep.id,
      name: dep.firstName + ' ' + dep.lastName
    }));
    if (dependents.value.length > 0 && !selectedDependent.value) {
      selectedDependent.value = dependents.value[0].id;
    }
  } catch (error) {
    console.error('Failed to load dependents:', error);
  }
}

async function loadCalendarData() {
  try {
    if (!selectedDependent.value) {
      calendarData.value = [];
      return;
    }
    calendarData.value = await medicationService.generateCalendarData(currentMonth.value, currentYear.value, selectedDependent.value);
  } catch (error) {
    console.error('Failed to load calendar data:', error);
  }
}

function goToPreviousMonth() {
  if (currentMonth.value === 1) {
    currentMonth.value = 12;
    currentYear.value--;
  } else {
    currentMonth.value--;
  }
}

function goToNextMonth() {
  if (currentMonth.value === 12) {
    currentMonth.value = 1;
    currentYear.value++;
  } else {
    currentMonth.value++;
  }
}

function selectDependent(depId) {
  selectedDependent.value = depId;
}

onMounted(async () => {
  const role = sessionStorage.getItem('role');
  if (role === 'care_giver') {
    await loadDependents();
    await loadCalendarData();
  } else {
    selectedDependent.value = sessionStorage.getItem('user_id');
    await loadCalendarData();
  }
});

watch([currentMonth, currentYear, selectedDependent], () => {
  loadCalendarData();
});
</script>

<style scoped>
/* All the CSS remains exactly the same as the previous version. */
.calendar-wrapper {
  padding: 1.5rem;
  background-color: #f8f9fa;
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #343a40;
  max-width: 600px;
  margin: 2rem auto;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e9ecef;
}

.arrow-button {
  font-size: 1.8rem;
  background: none;
  border: none;
  cursor: pointer;
  color: #007bff;
  transition: transform 0.2s ease, color 0.2s ease;
  padding: 0 10px;
}

.arrow-button:hover {
  transform: scale(1.2);
  color: #0056b3;
}

.calendar-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #495057;
  text-transform: capitalize;
}

.toggle-buttons {
  display: flex;
  justify-content: center;
  margin-bottom: 1.5rem;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.toggle-buttons button {
  padding: 0.5rem 1.25rem;
  border: 1px solid #007bff;
  background-color: #ffffff;
  border-radius: 25px;
  cursor: pointer;
  font-weight: 500;
  color: #007bff;
  transition: background-color 0.3s, color 0.3s;
}

.toggle-buttons .active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  box-shadow: 0 4px 10px rgba(0, 123, 255, 0.3);
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  text-align: center;
  margin-bottom: 0.75rem;
  font-weight: bold;
  color: #6c757d;
  font-size: 0.9rem;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 10px;
}

.calendar-cell {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 0.75rem;
  text-align: center;
  border: 1px solid #e9ecef;
  font-size: 0.9rem;
  min-height: 80px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s, box-shadow 0.2s;
}

.calendar-cell:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}

.calendar-cell.today {
  border: 2px solid #007bff;
  background-color: #e6f7ff;
}

.calendar-cell.future {
  opacity: 0.7;
  background-color: #f1f3f5;
  cursor: not-allowed;
}

.calendar-cell.past {
  background-color: #ffffff;
}

.cell-label {
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 0.25rem;
  color: #495057;
}

.calendar-cell.future .cell-label {
  color: #adb5bd;
}

.cell-data {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-top: auto;
}

.status-bar-container {
  display: flex;
  width: 100%;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
  background-color: #e9ecef;
}

.status-bar {
  height: 100%;
  transition: width 0.3s ease;
}

.status-bar.taken {
  background-color: #28a745;
}

.status-bar.missed {
  background-color: #dc3545;
}

.total-meds {
  font-size: 0.8rem;
  font-weight: 500;
  color: #6c757d;
  margin-top: 5px;
}
</style>
