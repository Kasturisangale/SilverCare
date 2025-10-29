<template>
  <div class="stats-dashboard-container">
    <Navbar />
    <header class="dashboard-header">
      <div class="header-left">
        <h1>Health at a Glance</h1>       
      </div>
      <div class="header-right">
        <div class="digital-clock">{{ currentTime }}</div>
        <button class="accessibility-btn" @click="cycleFontSize" title="Cycle Font Size">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16M4 18h16M4 6h16"/></svg>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12h16M4 18h16M4 6h16"/></svg>
        </button>
        
      </div>
    </header>

    <div class="member-toggle-group" v-if="role === 'care_giver' && members.length > 1">
      <button v-for="m in members" :key="m.username"
        class="toggle-button" :class="{ active: current === m.username }"
        @click="selectMember(m)">
        {{ m.username }}
      </button>
    </div>

    <div class="charts-row">
      <div class="chart-card">
        <h3>Medicine Compliance (Last 30 Days)</h3>
        <div class="chart-wrapper">
          <Bar :data="medicineChart" :options="barOptions"/>
        </div>
      </div>
      <div class="chart-card">
        <h3>Vitals (Last 7 Days)</h3>
        <div class="chart-wrapper">
          <Line :data="vitalsChart" :options="lineOptions"/>
        </div>
      </div>
    </div>
    
    <!-- Add Medicine Modal Placeholder -->
    <AddMedicineModal
      v-if="showAddMedicineModal"
      @close="showAddMedicineModal = false"
      @medication-added="fetchAllStats"
    />

    <!-- Custom Alert Modal for SOS -->
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from './Navbar.vue'
import AddMedicineModal from './AddMedicineModal.vue' // Assuming this component exists
import { Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS, Title, Tooltip, Legend,
  CategoryScale, LinearScale, BarElement, PointElement, LineElement
} from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, BarElement, PointElement, LineElement)

const router = useRouter()
const role = sessionStorage.getItem('role')
const uid = sessionStorage.getItem('user_id')
const token = sessionStorage.getItem('accesstoken')
const members = ref([])
const statsMap = ref({})
const current = ref(null)

// --- State for header features ---
const currentTime = ref('');
let clockInterval = null;
const fontSizeLevel = ref(0);
const showAddMedicineModal = ref(false);

// --- Alert State ---
const alertMessage = ref('');
const alertType = ref('info');

// --- Accessibility ---
watch(fontSizeLevel, (newLevel) => {
  let scale = 1;
  if (newLevel === 1) scale = 1.1;
  if (newLevel === 2) scale = 1.2;
  document.body.style.setProperty('--font-scale', scale);
}, { immediate: true });

function cycleFontSize() {
  fontSizeLevel.value = (fontSizeLevel.value + 1) % 3;
}



function updateTime() {
    currentTime.value = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

const medicineChart = computed(() => {
  const d = statsMap.value[current.value]?.medicineCompliance || {}
  return {
    labels: d.labels || [],
    datasets: [
      { label: 'Taken', backgroundColor: '#28a745', data: d.taken || [], borderRadius: 4 },
      { label: 'Missed', backgroundColor: '#dc3545', data: d.missed || [], borderRadius: 4 }
    ]
  }
})
const vitalsChart = computed(() => {
  const v = statsMap.value[current.value]?.vitalsLast7 || {}
  return {
    labels: v?.labels || [],
    datasets: [
      { label: 'Systolic', borderColor: '#007bff', data: v.systolic || [], fill: false, tension: 0.4 },
      { label: 'Diastolic', borderColor: '#6f42c1', data: v.diastolic || [], fill: false, tension: 0.4 },
      { label: 'Sugar', borderColor: '#fd7e14', data: v.sugar || [], fill: false, tension: 0.4 }
    ]
  }
})

const chartOptionsBase = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            labels: {
                font: { weight: 'bold', size: 16, family: "'Inter', sans-serif" },
                color: '#495057'
            }
        },
        tooltip: {
            titleFont: { weight: 'bold', size: 16, family: "'Inter', sans-serif" },
            bodyFont: { size: 14, family: "'Inter', sans-serif" }
        }
    },
    scales: {
        x: {
            title: {
                display: true,
                font: { weight: 'bold', size: 16, family: "'Inter', sans-serif" },
                color: '#6c757d'
            },
            ticks: {
                font: { weight: '500', size: 14, family: "'Inter', sans-serif" },
                color: '#495057'
            },
            grid: { display: false }
        },
        y: {
            beginAtZero: true,
            title: {
                display: true,
                font: { weight: 'bold', size: 16, family: "'Inter', sans-serif" },
                color: '#6c757d'
            },
            ticks: {
                font: { weight: '500', size: 14, family: "'Inter', sans-serif" },
                color: '#495057'
            },
            grid: { color: '#e9ecef' }
        }
    }
};

const barOptions = {
    ...chartOptionsBase,
    scales: {
        ...chartOptionsBase.scales,
        x: { ...chartOptionsBase.scales.x, stacked: true, title: { ...chartOptionsBase.scales.x.title, text: 'Medicines' } },
        y: { ...chartOptionsBase.scales.y, stacked: true, title: { ...chartOptionsBase.scales.y.title, text: 'Count' } }
    }
};

const lineOptions = {
    ...chartOptionsBase,
    scales: {
        ...chartOptionsBase.scales,
        x: { ...chartOptionsBase.scales.x, title: { ...chartOptionsBase.scales.x.title, text: 'Date' } },
        y: { ...chartOptionsBase.scales.y, beginAtZero: false, title: { ...chartOptionsBase.scales.y.title, text: 'Reading Value' } }
    }
};

function selectMember(m){ current.value = m.username }

async function fetchAllStats() {
  if (!uid || !token) return router.push('/login')
  if (role==='care_giver') {
    const dres = await fetch('http://localhost:5000/sc/my-dependents', {
      headers:{ 'Authorization':`Bearer ${token}` }
    })
    const { dependents } = await dres.json()
    members.value = dependents
    if (!dependents || dependents.length === 0) {
      return router.push('/manage-dependents')
    }
    for (const m of dependents) {
      const r = await fetch(`http://localhost:5000/sc/user-stats/${m.id}`, {
        headers:{ 'Authorization':`Bearer ${token}` }
      })
      statsMap.value[m.username] = await r.json()
    }
    if (!current.value) {
        current.value = members.value[0].username
    }
  }
  else if (role==='senior_citizen') {
    members.value = [{ id: uid, username: 'Me' }]
    const r = await fetch(`http://localhost:5000/sc/user-stats/${uid}`, {
      headers:{ 'Authorization':`Bearer ${token}` }
    })
    statsMap.value['Me'] = await r.json()
    current.value = 'Me'
  }
}


onMounted(() => {
  fetchAllStats();
  updateTime();
  clockInterval = setInterval(updateTime, 1000);
});

onUnmounted(() => {
    clearInterval(clockInterval);
});
</script>

<style scoped>
.stats-dashboard-container {
  background: url('https://images.unsplash.com/photo-1530305408560-82d13781b33a?q=80&w=2072&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  font-family: 'Inter', sans-serif;
  min-height: 100vh;
  padding: 2rem;
  padding-top: 100px; /* Space for fixed navbar */
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
.dashboard-header h1 {
  font-family: 'Georgia', serif;
  font-weight: 700;
  font-size: calc(2.8rem * var(--font-scale));
  margin: 0;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}
.dashboard-header p {
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

.accessibility-btn, .assign-btn, .sos-button {
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  font-weight: 600;
  font-size: calc(0.9rem * var(--font-scale));
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  letter-spacing: 0.5px;
}
.accessibility-btn {
    background-color: #6c757d;
    color: white;
    width: 44px;
    height: 44px;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 1rem;
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
.assign-btn {
  background-color: #007bff;
  color: white;
  margin-right: 1rem;
}
.sos-button {
  background-color: #dc3545;
  color: white;
}
.sos-button:disabled {
  background-color: #e7a1a1;
  cursor: not-allowed;
}

.member-toggle-group {
  margin-bottom: 2.5rem;
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  background-color: rgba(233, 236, 239, 0.9);
  padding: 0.5rem;
  border-radius: 50px;
  align-self: center;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}
.toggle-button {
  padding: 0.7rem 1.8rem;
  border: none;
  border-radius: 50px;
  background-color: transparent;
  font-weight: 600;
  font-size: calc(1.05rem * var(--font-scale));
  cursor: pointer;
  color: #495057;
  transition: all 0.3s ease;
}
.toggle-button.active {
  background-color: #fff;
  color: #007bff;
  box-shadow: 0 3px 10px rgba(0,0,0,0.1);
}

.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.chart-card {
  background-color: #ffffff;
  padding: 1.5rem 2rem;
  border-radius: 16px;
  border: 1px solid #dee2e6;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
}

.chart-card h3 {
  text-align: center;
  font-family: 'Georgia', serif;
  font-size: calc(1.4rem * var(--font-scale));
  font-weight: 600;
  color: #343a40;
  margin-bottom: 1.5rem;
}

.chart-wrapper {
  position: relative;
  height: 400px; /* Fixed height for consistency */
}

/* Custom Alert Styles */
.custom-alert-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
  background-color: rgba(0, 0, 0, 0.4); 
  display: flex; justify-content: center; align-items: center; 
  z-index: 3000;
}
.custom-alert-box {
  background: white;
  padding: 1.5rem 2rem 2rem 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 380px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}
.alert-icon-wrapper {
    margin-bottom: 1rem;
}
.custom-alert-box.success .alert-icon-wrapper { color: #28a745; }
.custom-alert-box.error .alert-icon-wrapper { color: #dc3545; }

.alert-title {
    font-size: calc(1.25rem * var(--font-scale));
    font-weight: 600;
    margin: 0 0 0.5rem 0;
}
.alert-message {
  margin: 0 0 1.5rem 0;
  font-size: calc(1rem * var(--font-scale));
  color: #6c757d;
  line-height: 1.6;
}
.alert-btn {
  padding: 10px 30px;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  font-size: calc(1rem * var(--font-scale));
}
.custom-alert-box.success .alert-btn { background-color: #28a745; }
.custom-alert-box.error .alert-btn { background-color: #dc3545; }
</style>
