<template>
  <div class="dashboard-wrapper" :class="fontSizeClass">
    <header class="dashboard-header">
      <div class="greeting"></div>
      <Navbar />
    </header>

    <div class="header">
      <div class="header-left">
        <br>
        <h2 class="greeting">Hi, {{ userName }}</h2>
        <p class="date">{{ formattedDate }}</p>
      </div>

      <div class="header-right">
        <!-- Digital Clock -->
        <div class="digital-clock">
          {{ currentTime }}
        </div>

        <button class="accessibility-btn" @click="cycleFontSize" title="Cycle Font Size">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16M4 18h16M4 6h16"/></svg>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16M4 18h16M4 6h16"/></svg>
        </button>
        <button class="assign-btn" @click="showAddMedicineModal = true">
          Assign Medicine
        </button>
        <button class="sos-button" @click="sendSOS" :disabled="sosLoading">
          {{ sosLoading ? '...' : 'SOS' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-state">
      <h3>{{ error }}</h3>
    </div>

    <div v-else class="main-content">
      <div class="left-panel">
        <div class="upcoming-meds-section">
            <h3 class="subheading">Next Up</h3>
            <div v-if="loading" class="med-card-placeholder">Loading...</div>
            <div v-else-if="upcomingMeds.length > 0">
              <div v-for="med in upcomingMeds" :key="med.medicineId" class="upcoming-med-card">
                <div class="med-item med-name-wrapper">
                  <div class="icon-wrapper alert-icon-bg">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
                  </div>
                  <svg class="med-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="5" width="10" height="14" rx="2" ry="2"></rect><path d="M9 5V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"></path><line x1="10" y1="12" x2="14" y2="12"></line><line x1="12" y1="10" x2="12" y2="14"></line></svg>
                  <span class="med-name">{{ med.medicineName }}</span>
                </div>
                <div class="med-item">
                  <span class="med-dosage">{{ med.dosage }}</span>
                </div>
                <div class="med-item">
                  <span class="med-time">{{ med.time }}</span>
                </div>
                <div class="med-item">
                  <button class="mark-taken-btn" @click="markMedicineTaken(med.medicineId, getSlot(med.slot))">
                    Mark as Taken
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="med-card empty">
              <p>No medications in the current window.</p>
            </div>
        </div>

        <div class="todays-meds-section">
            <h3 class="subheading">Today's Schedule</h3>
            <div v-if="loading" class="med-card-placeholder">Loading schedule...</div>
            <div v-else class="todays-meds-container">
              <div class="meds-category">
                <div class="category-header">
                  <div class="icon-wrapper day-icon-bg">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                  </div>
                  <span>Daytime Meds</span>
                </div>
                <p v-if="daytimeMeds.length === 0" class="no-meds-text">No daytime medications scheduled.</p>
                <div v-else class="med-list">
                  <div v-for="med in daytimeMeds" :key="med.id" class="med-card">
                      <div class="med-item med-name-wrapper">
                        <svg class="med-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="5" width="10" height="14" rx="2" ry="2"></rect><path d="M9 5V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"></path><line x1="10" y1="12" x2="14" y2="12"></line><line x1="12" y1="10" x2="12" y2="14"></line></svg>
                        <span class="med-name">{{ med.medicine_name || med.title }}</span>
                      </div>
                      <div class="med-item">
                        <span class="med-dosage">{{ med.dosage }}</span>
                      </div>
                      <div class="med-item">
                        <span class="med-time">{{ med.times.join(", ") }}</span>
                      </div>
                  </div>
                </div>
              </div>

              <div class="meds-category">
                <div class="category-header">
                  <div class="icon-wrapper night-icon-bg">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                  </div>
                  <span>Nighttime Meds</span>
                </div>
                <p v-if="nighttimeMeds.length === 0" class="no-meds-text">No nighttime medications scheduled.</p>
                <div v-else class="med-list">
                  <div v-for="med in nighttimeMeds" :key="med.id" class="med-card">
                      <div class="med-item med-name-wrapper">
                        <svg class="med-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="5" width="10" height="14" rx="2" ry="2"></rect><path d="M9 5V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"></path><line x1="10" y1="12" x2="14" y2="12"></line><line x1="12" y1="10" x2="12" y2="14"></line></svg>
                        <span class="med-name">{{ med.medicine_name || med.title || '-' }}</span>
                      </div>
                      <div class="med-item">
                        <span class="med-dosage">{{ med.dosage || '-' }}</span>
                      </div>
                      <div class="med-item">
                        <span class="med-time">{{ med.times.join(", ") }}</span>
                      </div>
                  </div>
                </div>
              </div>
            </div>
        </div>
      </div>

      <div class="right-panel">
        <p class="motivational-quote">"The best way to predict the future is to create it."</p>
        <MusicPlayer />
        <AppCalendar />
      </div>

      <AddMedicineModal
        v-if="showAddMedicineModal"
        @close="showAddMedicineModal = false"
        @add-medication="handleAddMedication"
      />

      <div v-if="sosMessage" class="sos-alert" @click="sosMessage = ''">{{ sosMessage }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import Navbar from './Navbar.vue';
import AppCalendar from './AppCalendar.vue';
import apiService from '@/services/apiService';
import MusicPlayer from './MusicPlayer.vue';
import AddMedicineModal from './AddMedicineModal.vue';

const userName = ref(sessionStorage.getItem('user_name') || 'User');
const upcomingMeds = ref([]);
const daytimeMeds = ref([]);
const nighttimeMeds = ref([]);
const loading = ref(true);
const error = ref(null);
const sosLoading = ref(false);
const sosMessage = ref('');
const showAddMedicineModal = ref(false);

const fontSizeLevel = ref(0);
const currentTime = ref('');
let clockInterval = null;

const fontSizeClass = computed(() => `font-size-level-${fontSizeLevel.value}`);

function cycleFontSize() {
  fontSizeLevel.value = (fontSizeLevel.value + 1) % 3;
}

const formattedDate = computed(() =>
  new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
  })
);
const slotMap = {
  "Breakfast before": "breakfast_before",
  "Breakfast after": "breakfast_after",
  "Lunch before": "lunch_before",
  "Lunch after": "lunch_after",
  "Dinner before": "dinner_before",
  "Dinner after": "dinner_after"
};

function getSlot(reminderSlot) {
  if (!reminderSlot) return null;
  return slotMap[reminderSlot] || slotMap[reminderSlot.charAt(0).toUpperCase() + reminderSlot.slice(1)] || null;
}

function updateTime() {
    currentTime.value = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

async function getUpcomingMedication() {
  try {
    const res = await apiService.get('/sc/upcoming-medications');
    const data = res.data;

    if (res.status === 200) {
      return {
        success: true,
        meds: data.upcoming_medications || [],
        count: data.count || 0,
      };
    } else {
      return {
        success: false,
        message: data.error || data.message || "Failed to get medications",
      };
    }
  } catch (err) {
    if (err.response && err.response.status === 404) {
      return {
        success: true,
        meds: [],
        count: 0,
      };
    }
    console.error("🔴 Error fetching upcoming medications:", err);
    return {
      success: false,
      message: err.message,
    };
  }
}

async function fetchAllDataForSenior() {
  loading.value = true;
  error.value = null;
  try {
    const response = await getUpcomingMedication();
    if (!response.success) throw new Error(response.message);

    upcomingMeds.value = response.meds.map(med => ({
      medicineId: med.medicine_id,
      medicineName: med.medicine_title,
      dosage: med.dosage,
      time: med.reminder_slot,
      slot: med.reminder_slot
    }));

    const todayRes = await apiService.get('/sc/todays-medications');
    if (todayRes.status === 200 && todayRes.data.medications) {
      daytimeMeds.value = todayRes.data.medications.filter(m => m.category === 'daytime');
      nighttimeMeds.value = todayRes.data.medications.filter(m => m.category === 'nighttime');
    } else {
      daytimeMeds.value = [];
      nighttimeMeds.value = [];
    }
  } catch (err) {
    error.value = "No medicines yet — click Assign Medicine to get started.";
  } finally {
    loading.value = false;
  }
}

async function assignMedicineSchedule(payload) {
  try {
    const requestBody = { ...payload };
    const response = await apiService.post('/sc/assign-medicine', requestBody);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('Error assigning medicine schedule:', error.response?.data || error.message);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Failed to assign medicine schedule',
      validationErrors: error.response?.data?.errors || null,
    };
  }
}

async function handleAddMedication(payload) {
  showAddMedicineModal.value = false;
  const finalPayload = { ...payload };
  console.log('Payload sent:', finalPayload);
  const result = await assignMedicineSchedule(finalPayload);

  if (result.success) {
    alert('Medicine assigned successfully.');
    fetchAllDataForSenior();
  } else {
    console.error('Validation errors:', result.validationErrors);
    alert('Failed to assign medicine: ' + result.error);
  }
}

async function markMedicineTaken(medicineId, slot) {
  console.log("Medicine ID:", medicineId);
  console.log("Slot:", slot);

  const validSlots = [
    "breakfast_before", "breakfast_after",
    "lunch_before", "lunch_after",
    "dinner_before", "dinner_after"
  ];

  if (!medicineId || !slot || !validSlots.includes(slot)) {
    alert(`Invalid medicine or slot value: ${slot}`);
    return;
  }

  try {
    const res = await apiService.put('/sc/mark-medicine-taken', {
      medicine_id: medicineId,
      slot: slot,
    });

    if (res.status === 200) {
      alert('Medicine marked as taken.');
      fetchAllDataForSenior();
    } else {
      alert('Failed to mark medicine as taken.');
    }
  } catch (error) {
    console.error('Error marking medicine as taken:', error);
    alert(error.response?.data?.error || 'Error marking medicine as taken.');
  }
}

async function sendSOS() {
  sosLoading.value = true
  sosMessage.value = ''

  try {
    const res = await apiService.post('/sc/send-sos')
    if (res.status === 200 && res.data.status === 'SOS sent successfully') {
      console.log('✅ SOS Alert Sent:', res.data.alerts_sent)
      sosMessage.value = '🚨 SOS Alert sent to your caregivers.'
    } else {
      sosMessage.value = res.data.message || '⚠️ Could not send SOS alert.'
    }
  } catch (err) {
    console.error('❌ Error sending SOS:', err)
    sosMessage.value = err.response?.data?.error || '❌ Failed to send SOS alert.'
  } finally {
    sosLoading.value = false
    setTimeout(() => {
      sosMessage.value = ''
    }, 4000)
  }
}

onMounted(() => {
  fetchAllDataForSenior();
  updateTime();
  clockInterval = setInterval(updateTime, 1000);
});

onUnmounted(() => {
    clearInterval(clockInterval);
});
</script>

<style scoped>
.right-panel {
  position: sticky;
  top: 2rem;
  display: flex;
  flex-direction: column;
}

.motivational-quote {
  margin-bottom: 1.5rem;
  background-color: #e9ecef;
  border-left: 4px solid #007bff;
  padding: 1rem;
  border-radius: 8px;
  font-style: italic;
  color: #495057;
  font-size: calc(0.95rem * var(--font-scale));
}
.dashboard-wrapper {
  --font-scale: 1;

  background: url('https://images.unsplash.com/photo-1530305408560-82d13781b33a?q=80&w=2072&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;

  min-height: 100vh;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  padding: 2rem;
  transition: font-size 0.3s ease;
}

.dashboard-wrapper.font-size-level-0 { --font-scale: 1; }
.dashboard-wrapper.font-size-level-1 { --font-scale: 1.1; }
.dashboard-wrapper.font-size-level-2 { --font-scale: 1.2; }


.header {
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
.header-left .greeting {
  font-family: 'Georgia', serif;
  font-size: calc(2.2rem * var(--font-scale));
  margin: 0;
  color: #e7ebee;
}
.header-left .date {
  font-size: calc(1rem * var(--font-scale));
  color: #e0e0e0;
  margin-top: 0.25rem;
}

.header-right {
    display: flex;
    align-items: center;
    flex: 1;
    justify-content: flex-end;
    min-width: 300px;
}

.subheading {
  font-weight: 600;
  color: #343a40;
  font-size: calc(1.2rem * var(--font-scale));
  margin: 0 0 1rem 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #dee2e6;
}

.main-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  align-items: flex-start;
}

.left-panel {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* --- Digital Clock --- */
.digital-clock {
    background-color: rgba(255, 255, 255, 0.9);
    padding: 0.75rem 1.5rem;
    border-radius: 12px;
    font-family: 'Courier New', Courier, monospace;
    font-size: calc(2rem * var(--font-scale));
    font-weight: 700;
    color: #343a40;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    margin-right: 10rem; /* Pushes it to the right */
}

/* --- Buttons --- */
.accessibility-btn {
    background-color: #6c757d;
    color: white;
    border: none;
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    margin-right: 1rem;
    transition: all 0.2s ease-in-out;
}
.accessibility-btn:hover {
    background-color: #5a6268;
    transform: translateY(-2px);
}
.accessibility-btn svg {
    width: 16px;
    height: 16px;
}
.accessibility-btn svg:first-child {
    width: 12px;
    height: 12px;
    margin-right: 2px;
}

.assign-btn, .sos-button {
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
  font-size: calc(0.9rem * var(--font-scale));
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  letter-spacing: 0.5px;
}

.assign-btn {
  background-color: #007bff;
  color: white;
  margin-right: 1rem;
}
.assign-btn:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
}

.sos-button {
  background-color: #dc3545;
  color: white;
}
.sos-button:hover {
  background-color: #c82333;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 53, 69, 0.2);
}
.sos-button:disabled {
  background-color: #e7a1a1;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* --- Medication Card Styles --- */
.upcoming-meds-section, .todays-meds-section {
    background-color: #ffffff;
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid #e9ecef;
    box-shadow: 0 4px 6px rgba(0,0,0,0.03);
}

.icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.upcoming-med-card {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr auto;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1rem;
  background-color: #e7f3ff;
  border: 1px solid #b3d7ff;
}
.med-item {
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
}
.med-name-wrapper {
    justify-content: flex-start;
    gap: 1rem; /* Increased gap */
}
.icon-wrapper.alert-icon-bg {
    margin-right: 0.5rem; /* Space between icons */
}
.med-icon {
    color: #004085;
}

.upcoming-med-card .med-name {
    font-size: calc(1.2rem * var(--font-scale)); /* Increased font size */
    font-weight: 700;
}
.upcoming-med-card .med-dosage {
    font-size: calc(1rem * var(--font-scale)); /* Increased font size */
    color: #495057;
}

.todays-meds-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.meds-category {
  background-color: transparent;
  padding: 0;
  border: none;
  box-shadow: none;
}

.category-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: calc(1.1rem * var(--font-scale));
  font-weight: 600;
  color: #343a40;
  margin-bottom: 1rem;
}
.category-header .icon-wrapper {
    width: 38px;
    height: 38px;
}

.day-icon-bg { background-color: #fff4d5; color: #ffc107; }
.night-icon-bg { background-color: #e9e7fd; color: #6f42c1; }

.med-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.med-card {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1rem;
  border-radius: 10px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
}

.med-card.empty {
  display: flex;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  color: #6c757d;
  background-color: #f8f9fa;
  border: 1px dashed #ced4da;
}

.med-name {
  font-weight: 700; /* Bolder */
  color: #212529;
  font-size: calc(1.05rem * var(--font-scale)); /* Increased font size */
}

.med-dosage {
  font-size: calc(0.9rem * var(--font-scale)); /* Increased font size */
  color: #6c757d;
}

.med-time {
  font-weight: 600; /* Bolder */
  color: #495057;
  font-size: calc(0.95rem * var(--font-scale)); /* Increased font size */
  background-color: #e9ecef;
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
}

.no-meds-text {
  font-style: italic;
  color: #6c757d;
  text-align: center;
  padding: 1rem 0;
  font-size: calc(0.9rem * var(--font-scale));
}

.mark-taken-btn {
  background-color: #28a745;
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
  font-size: calc(0.85rem * var(--font-scale));
  white-space: nowrap;
  transition: background-color 0.2s ease;
}

.mark-taken-btn:hover {
  background-color: #218838;
}

@media (max-width: 992px) {
    .main-content {
        grid-template-columns: 1fr;
    }
    .right-panel {
        position: static;
    }
    .header {
        gap: 1.5rem;
    }
    .header-left, .header-right {
        flex-basis: 45%;
    }
    .digital-clock {
        order: -1;
        flex-basis: 100%;
        text-align: center;
    }
}

@media (max-width: 768px) {
    .header {
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
    }
    .header-left, .header-right {
        text-align: center;
        width: 100%;
        justify-content: center;
    }
    .todays-meds-container {
        grid-template-columns: 1fr;
    }
}
</style>
