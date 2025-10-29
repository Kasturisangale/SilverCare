<template>
  <div class="dashboard-wrapper" :class="fontSizeClass">
    <Navbar />
    <header class="dashboard-header">
      <div class="header-left">
        <h1>Welcome back, {{ caregiverName }} </h1>
        
      </div>
      <div class="header-right">
        <div class="digital-clock">{{ currentTime }}</div>
        <button class="accessibility-btn" @click="cycleFontSize" title="Cycle Font Size">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16M4 18h16M4 6h16"/></svg>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16M4 18h16M4 6h16"/></svg>
        </button>
      </div>
    </header>

    <main class="main-content">
      <div class="medications-column">
        <div v-if="loading" class="loading-state">Loading dependents...</div>
        <div v-else-if="dependents.length === 0" class="empty-state">
          <h3>No Dependents Found</h3>
          <p>It looks like you haven’t added any dependents yet.</p>
          <router-link to="/manage-dependents" class="add-dependent-link">Add a Dependent</router-link>
        </div>
        <div v-else>
          <div v-for="dependent in dependents" :key="dependent.id" class="dependent-card">
            <header class="dependent-header">
              <h3>{{ dependent.username }}'s Next Medications</h3>
              <a href="#" class="view-all-link" @click.prevent="openMedicationModal(dependent)">View All</a>
            </header>

            <div v-if="dependent.medications && dependent.medications.length > 0" class="med-list">
              <div v-for="med in dependent.medications" :key="med.medicine_id" class="med-info-card">
                <div class="med-item med-name-wrapper">
                    <div class="icon-wrapper time-of-day-icon" :class="isDaytime(med.reminder_slot) ? 'day' : 'night'">
                        <svg v-if="isDaytime(med.reminder_slot)" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                    </div>
                    <svg class="med-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="5" width="10" height="14" rx="2" ry="2"></rect><path d="M9 5V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"></path><line x1="10" y1="12" x2="14" y2="12"></line><line x1="12" y1="10" x2="12" y2="14"></line></svg>
                    <span class="med-name">{{ med.medicine_title }}</span>
                </div>
                <span class="med-item med-dosage">{{ med.dosage }}</span>
                <span class="med-item med-time">{{ med.reminder_slot }}</span>
                <button class="poke-button" :disabled="!isPokeEnabled(med.reminder_slot)" @click="poke(dependent,med)">
                  Poke
                </button>
              </div>
            </div>
            <div v-else class="no-meds-notice">
                <p>No upcoming medications for {{ dependent.username }}.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="calendar-column">
        <AppCalendar />
      </div>
    </main>

    <!-- Medication Modal -->
    <div v-if="isModalVisible" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
            <h3 class="modal-title">{{ selectedDependent.username }}'s Medications</h3>
            <button class="close-btn" @click="closeModal">&times;</button>
        </div>
        <div class="modal-body">
            <div v-if="isModalLoading" class="modal-loading">Loading medications...</div>
            <div v-else class="modal-meds-list">
              <div class="modal-meds-category">
                <div class="category-header">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                    <h4>Daytime Meds</h4>
                </div>
                <p v-if="modalMeds.daytime.length === 0" class="no-meds-text">No daytime medications scheduled.</p>
                <div v-else v-for="med in modalMeds.daytime" :key="med.id" class="modal-med-card">
                  <span class="med-name">{{ med.medicine_name }}</span>
                  <span class="med-dosage">{{ med.dosage }}</span>
                  <span class="med-time">{{ med.times.join(', ') }}</span>
                </div>
              </div>
              <div class="modal-meds-category">
                <div class="category-header">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                    <h4>Nighttime Meds</h4>
                </div>
                <p v-if="modalMeds.nighttime.length === 0" class="no-meds-text">No nighttime medications scheduled.</p>
                <div v-else v-for="med in modalMeds.nighttime" :key="med.id" class="modal-med-card">
                  <span class="med-name">{{ med.medicine_name }}</span>
                  <span class="med-dosage">{{ med.dosage }}</span>
                  <span class="med-time">{{ med.times.join(', ') }}</span>
                </div>
              </div>
            </div>
        </div>
        <div class="modal-actions">
            <button class="modal-btn-cancel" @click="closeModal">Close</button>
        </div>
      </div>
    </div>

    <!-- Custom Alert for Poke -->
     <div v-if="alertMessage" class="custom-alert-overlay" @click.self="alertMessage = ''">
      <div class="custom-alert-box" :class="alertType">
        <div class="alert-icon-wrapper">
          <svg v-if="alertType === 'success'" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
          <svg v-if="alertType === 'error'" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
        </div>
        <h3 class="alert-title">{{ alertType.charAt(0).toUpperCase() + alertType.slice(1) }}</h3>
        <p class="alert-message">{{ alertMessage }}</p>
        <button class="alert-btn" @click="alertMessage = ''">OK</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import Navbar from './Navbar.vue';
import AppCalendar from '@/components/AppCalendar.vue';
import { fetchMyDependents } from '@/services/profileService';
import apiService from '@/services/apiService';

const caregiverName = ref(sessionStorage.getItem('user_name') || 'Caregiver');
const dependents = ref([]);
const loading = ref(true);

const isModalVisible = ref(false);
const selectedDependent = ref(null);
const modalMeds = ref({ daytime: [], nighttime: [] });
const isModalLoading = ref(false);

// --- New State ---
const currentTime = ref('');
let clockInterval = null;
const fontSizeLevel = ref(0);
const alertMessage = ref('');
const alertType = ref('info');

const fontSizeClass = computed(() => `font-size-level-${fontSizeLevel.value}`);

function cycleFontSize() {
  fontSizeLevel.value = (fontSizeLevel.value + 1) % 3;
}

watch(fontSizeLevel, (newLevel) => {
  let scale = 1;
  if (newLevel === 1) scale = 1.1;
  if (newLevel === 2) scale = 1.2;
  document.body.style.setProperty('--font-scale', scale);
}, { immediate: true });

function updateTime() {
    currentTime.value = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

function isDaytime(slot) {
    if (!slot) return true;
    const slotLower = slot.toLowerCase();
    return slotLower.includes('breakfast') || slotLower.includes('lunch');
}

async function fetchAllDependentsData() {
  loading.value = true;
  try {
    dependents.value = await fetchMyDependents() || [];
    if (!dependents.value.length) {
      loading.value = false;
      return; 
    }

    const upcomingRes = await apiService.get('/sc/upcoming-medications');
    const upcomingAll = upcomingRes.data?.upcoming_medications || [];

    const todayRes = await apiService.get('/sc/todays-medications');
    const todayAll = todayRes.data?.medications || [];

    dependents.value = dependents.value.map((dep) => {
      return {
        ...dep,
        medications: upcomingAll.filter(m => m.user_id === dep.id),
        todayDaytime: todayAll.filter(m => m.category === 'daytime' && m.user_id === dep.id),
        todayNighttime: todayAll.filter(m => m.category === 'nighttime' && m.user_id === dep.id)
      };
    });
  } catch (err) {
    console.error('Error fetching dependents data:', err);
    dependents.value = [];
  } finally {
    loading.value = false;
  }
}

function isPokeEnabled(slot) {
  const hour = new Date().getHours();
  if (!slot) return false;
  const slotLower = slot.toLowerCase();
  if (slotLower.includes('breakfast')) return hour >= 4 && hour <= 10;
  if (slotLower.includes('lunch')) return hour >= 10 && hour <= 15;
  if (slotLower.includes('dinner')) return hour >= 16 && hour <= 23;
  return false;
}

function showAlert(message, type = 'success') {
    alertMessage.value = message;
    alertType.value = type;
}

function poke(dependent, med) {
  apiService.post('/sc/send-poke', {
    senior_id: dependent.id,
    medicine_id: med.medicine_id,
    slot: med.reminder_slot
  }).then(() => {
    showAlert(`A reminder has been sent to ${dependent.username}.`, 'success');
  }).catch(err => {
    showAlert(`Failed to send reminder to ${dependent.username}.`, 'error');
    console.error('Error sending poke:', err);
  });
}

function openMedicationModal(dependent) {
  if (!dependent) return;
  selectedDependent.value = dependent;
  isModalVisible.value = true;
  modalMeds.value = {
    daytime: dependent.todayDaytime || [],
    nighttime: dependent.todayNighttime || []
  };
}

function closeModal() {
  isModalVisible.value = false;
  selectedDependent.value = null;
}

onMounted(() => {
  fetchAllDependentsData();
  updateTime();
  clockInterval = setInterval(updateTime, 1000);
});

onUnmounted(() => {
    clearInterval(clockInterval);
});
</script>

<style scoped>
.dashboard-wrapper {
  background: url('https://images.unsplash.com/photo-1530305408560-82d13781b33a?q=80&w=2072&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  padding: 2rem;
  padding-top: 100px;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}
.header-left {
    flex: 1;
    min-width: 250px;
}
.header-left h1 {
  font-family: 'Georgia', serif;
  font-weight: 700;
  font-size: calc(2.8rem * var(--font-scale));
  margin: 0;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}
.header-left p {
  font-size: calc(1.2rem * var(--font-scale));
  color: #e0e0e0;
  margin-top: 0.5rem;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}
.header-right {
    display: flex;
    align-items: center;
    flex: 1;
    justify-content: flex-end;
    min-width: 300px;
}

.digital-clock {
    background-color: rgba(255, 255, 255, 0.9);
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-family: 'Courier New', Courier, monospace;
    font-size: calc(2rem * var(--font-scale));
    font-weight: 700;
    color: #343a40;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-right: 1.5rem;
}

.accessibility-btn {
    background-color: #6c757d;
    color: white;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    margin-right: 1rem;
    border: none;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  align-items: flex-start;
}

.medications-column {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dependent-card {
  background-color: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  margin-bottom: 1rem; /* Space between cards */
}

.dependent-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 1rem;
}
.dependent-header h3 {
    font-family: 'Georgia', serif;
    font-size: 1.4rem;
    font-weight: 600;
}

.view-all-link {
  font-size: 0.9rem;
  color: #007bff;
  font-weight: 600;
  text-decoration: none;
}

.med-info-card {
  display: grid;
  grid-template-columns: 2.5fr 1fr 1.5fr auto;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  margin-bottom: 0.75rem;
  background-color: #e7f3ff;
  border: 1px solid #b3d7ff;
}

.med-item {
    display: flex;
    align-items: center;
    justify-content: center;
}

.med-name-wrapper {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    justify-content: flex-start;
}
.icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    margin-right: 0.5rem;
}
.icon-wrapper.day { background-color: #fff4d5; color: #ffc107; }
.icon-wrapper.night { background-color: #e9e7fd; color: #6f42c1; }

.med-icon {
    color: #0056b3;
}
.med-name {
  font-weight: 700;
  font-size: calc(1.1rem * var(--font-scale));
}
.med-dosage {
    font-size: calc(1rem * var(--font-scale));
}
.med-time {
    font-size: calc(1rem * var(--font-scale));
}

.poke-button {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 0.5rem 1rem;
  font-weight: bold;
  font-size: 0.9rem;
  cursor: pointer;
}
.poke-button:disabled {
  background-color: #f1b0b7;
  cursor: not-allowed;
}

.empty-state {
    background-color: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
}
.add-dependent-link {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.6rem 1.2rem;
    background-color: #28a745;
    color: white;
    text-decoration: none;
    border-radius: 50px;
    font-weight: 600;
}

/* Modal Styles */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 0; border-radius: 12px; width: 90%; max-width: 600px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); display: flex; flex-direction: column; max-height: 80vh; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; }
.modal-title { font-size: 1.5rem; font-weight: 600; margin: 0; }
.close-btn { background: none; border: none; font-size: 2rem; line-height: 1; color: #6c757d; cursor: pointer; }
.modal-body { overflow-y: auto; padding: 1.5rem; }
.modal-meds-category { margin-bottom: 1.5rem; }
.category-header { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; font-size: 1.2rem; font-weight: 600; }
.modal-med-card { display: grid; grid-template-columns: 2fr 1fr 2fr; gap: 1rem; padding: 0.8rem 1rem; border-radius: 10px; margin-bottom: 0.5rem; background-color: #f8f9fa; }
.modal-actions { display: flex; justify-content: flex-end; padding: 1rem 1.5rem; border-top: 1px solid #dee2e6; background-color: #f8f9fa; }
.modal-btn-cancel { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 0.95rem; font-weight: 600; background-color: #6c757d; color: white; }

/* Custom Alert Styles */
.custom-alert-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.4); display: flex; justify-content: center; align-items: center; z-index: 3000; }
.custom-alert-box { background: white; padding: 1.5rem 2rem 2rem 2rem; border-radius: 12px; width: 90%; max-width: 380px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
.alert-icon-wrapper { margin-bottom: 1rem; }
.custom-alert-box.success .alert-icon-wrapper { color: #28a745; }
.custom-alert-box.error .alert-icon-wrapper { color: #dc3545; }
.alert-title { font-size: 1.25rem; font-weight: 600; margin: 0 0 0.5rem 0; }
.alert-message { margin: 0 0 1.5rem 0; font-size: 1rem; color: #6c757d; line-height: 1.6; }
.alert-btn { padding: 10px 30px; border: none; border-radius: 8px; color: white; font-weight: 600; cursor: pointer; width: 100%; font-size: 1rem; }
.custom-alert-box.success .alert-btn { background-color: #28a745; }
.custom-alert-box.error .alert-btn { background-color: #dc3545; }
</style>
