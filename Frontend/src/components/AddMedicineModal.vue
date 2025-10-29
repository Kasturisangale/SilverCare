<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Add Medicine Schedule</h2>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      
      <div class="modal-body">
        <!-- Step 1: Search for a medicine -->
        <div class="form-step">
          <label class="step-label">1. Find or create a medicine</label>
          <div class="search-wrapper">
            <input type="text" v-model="searchQuery" placeholder="Search for medicine name..." @input="handleSearch" />
            <div v-if="isSearching" class="spinner"></div>
          </div>
          
          <ul v-if="searchResults.length > 0 && !selectedMedicine" class="search-results">
            <li v-for="med in searchResults" :key="med.id" @click="selectMedicine(med)">
              {{ med.title }}
            </li>
          </ul>

          <div v-if="searchAttempted && searchResults.length === 0 && !isSearching" class="search-status">
            <p>No medicine found named "{{ searchQuery }}".</p>
            <button class="create-new-btn" @click="openRequestModal(searchQuery)" :disabled="!searchQuery.trim()">
              Request to Add
            </button>
          </div>
          
          <div v-if="selectedMedicine" class="selected-medicine">
            <span>Selected: <strong>{{ selectedMedicine.title }}</strong></span>
            <button @click="clearSelection">Change</button>
          </div>
        </div>
        
        <!-- Step 2: Define Dosage and Schedule -->
        <div class="form-step" :class="{ disabled: !selectedMedicine }">
          <label class="step-label">2. Set dosage and schedule</label>
          <input type="text" v-model="dosage" placeholder="e.g., 1 pill, 10mg" />

          <div class="date-picker">
            <div>
              <label>Start Date</label>
              <input type="date" v-model="startDate" />
            </div>
            <div>
              <label>End Date (optional)</label>
              <input type="date" v-model="endDate" />
            </div>
          </div>
          
          <div class="schedule-grid">
            <div class="meal-group">
              <h4>Breakfast</h4>
              <label class="custom-checkbox"><input type="checkbox" v-model="schedule.breakfast_before"> Before</label>
              <label class="custom-checkbox"><input type="checkbox" v-model="schedule.breakfast_after"> After</label>
            </div>
            <div class="meal-group">
              <h4>Lunch</h4>
              <label class="custom-checkbox"><input type="checkbox" v-model="schedule.lunch_before"> Before</label>
              <label class="custom-checkbox"><input type="checkbox" v-model="schedule.lunch_after"> After</label>
            </div>
            <div class="meal-group">
              <h4>Dinner</h4>
              <label class="custom-checkbox"><input type="checkbox" v-model="schedule.dinner_before"> Before</label>
              <label class="custom-checkbox"><input type="checkbox" v-model="schedule.dinner_after"> After</label>
            </div>
          </div>
        </div>
      </div>

      <!-- Actions -->
      <div class="modal-actions">
        <button class="modal-btn-cancel" @click="$emit('close')">Cancel</button>
        <button class="modal-btn-confirm" @click="submit" v-if="selectedMedicine" :disabled="!isFormValid">Add to Schedule</button>
      </div>
    </div>

    <!-- Nested Request Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
        <div class="modal-content request-modal-box">
            <div class="modal-header">
                <h3>Request New Medicine</h3>
                <button class="close-btn" @click="showModal = false">&times;</button>
            </div>
            <div class="modal-body">
              <label>Title</label>
              <input v-model="requestTitle" type="text" required />
              <label>Description</label>
              <textarea v-model="requestDescription" required placeholder="Enter description"></textarea>
            </div>
            <div class="modal-actions">
                <button class="modal-btn-cancel" @click="showModal = false">Cancel</button>
                <button class="modal-btn-confirm" @click="submitRequest">Submit Request</button>
            </div>
        </div>
    </div>

    <!-- Custom Alert Modal -->
    <div v-if="alertMessage" class="custom-alert-overlay" @click.self="alertMessage = ''">
      <div class="custom-alert-box" :class="alertType">
        <div class="alert-icon-wrapper">
          <svg v-if="alertType === 'success'" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
          <svg v-if="alertType === 'error'" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
          <svg v-if="alertType === 'info'" xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        </div>
        <h3 class="alert-title">{{ alertType.charAt(0).toUpperCase() + alertType.slice(1) }}</h3>
        <p class="alert-message">{{ alertMessage }}</p>
        <button class="alert-btn" @click="alertMessage = ''">OK</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, reactive, computed, defineEmits } from 'vue'
import apiService from '@/services/apiService'

const showModal = ref(false)
const requestTitle = ref('')
const requestDescription = ref('')
const selectedMedicineTitle = ref('')

const emit = defineEmits(['close', 'medication-added']) // Updated emit

// --- State ---
const searchQuery = ref('')
const searchResults = ref([])
const isSearching = ref(false)
const searchAttempted = ref(false)

const selectedMedicine = ref(null)
const dosage = ref('')
const startDate = ref('')
const endDate = ref('')
const schedule = reactive({
  breakfast_before: false,
  breakfast_after: false,
  lunch_before: false,
  lunch_after: false,
  dinner_before: false,
  dinner_after: false,
})

// --- Custom Alert State ---
const alertMessage = ref('');
const alertType = ref('info'); // 'info', 'success', 'error'

// --- Computed ---
const isFormValid = computed(() => {
  const hasSchedule = Object.values(schedule).some(v => v)
  return selectedMedicine.value && dosage.value.trim() && hasSchedule && startDate.value
})

// --- Methods ---
function showAlert(message, type = 'info') {
  alertMessage.value = message;
  alertType.value = type;
}

let searchTimeout

async function handleSearch() {
  clearTimeout(searchTimeout)
  isSearching.value = true
  searchAttempted.value = true

  searchTimeout = setTimeout(async () => {
    try {
      const res = await apiService.get('/sc/all-medicines')
      const data = res.data
      const query = searchQuery.value.toLowerCase()

      searchResults.value = data.medicines.filter(med =>
        med.title.toLowerCase().includes(query)
      )
    } catch (err) {
      console.error('Search error:', err)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }, 300)
}

function openRequestModal(title) {
  selectedMedicineTitle.value = title
  requestTitle.value = title
  requestDescription.value = ''
  showModal.value = true
}

async function submitRequest() {
  if (!requestTitle.value.trim() || !requestDescription.value.trim()) {
    showAlert('Please fill in both title and description.', 'error');
    return
  }

  try {
    const res = await apiService.post('/sc/create-medicine', {
      title: requestTitle.value,
      description: requestDescription.value,
    })

    const data = res.data

    if (res.status === 201 || data.success) {
      showAlert('Request submitted successfully!', 'success');
      showModal.value = false
    } else {
      showAlert(data.error || 'Request failed', 'error');
    }
  } catch (err) {
    console.error('Error submitting request:', err.message)
    showAlert('Something went wrong', 'error');
  }
}

function selectMedicine(med) {
  selectedMedicine.value = med
}

function clearSelection() {
  selectedMedicine.value = null
  searchQuery.value = ''
  searchResults.value = []
  searchAttempted.value = false
}

async function submit() {
  if (!isFormValid.value) return;

  if (!startDate.value) {
    showAlert("Please select a start date.", 'error');
    return;
  }
  if (/^\d+$/.test(dosage.value.trim())) {
    showAlert("Dosage must include units or description (e.g., '1 pill', '10mg').", 'error');
    return;
  }
  if (endDate.value && endDate.value < startDate.value) {
      showAlert("End date cannot be before the start date.", 'error');
      return;
  }

  const payload = {
    medicine_id: selectedMedicine.value.id,
    dosage: dosage.value,
    start_date: startDate.value,
    ...(endDate.value ? { end_date: endDate.value } : {}),
    ...schedule,
  };

  // ✅ Include end_date only if it's filled
  if (endDate.value && endDate.value >= startDate.value) {
    payload.end_date = endDate.value;
  }

  console.log("✅ Emitting payload with dates:", payload);
  emit('add-medication', payload);
}

</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
  background-color: rgba(0, 0, 0, 0.6); 
  display: flex; justify-content: center; align-items: center; 
  z-index: 1000;
  font-family: 'Inter', sans-serif;
}
.modal-content {
  background: white; padding: 0; border-radius: 12px; 
  width: 90%; max-width: 550px; /* Made smaller */
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 90vh; /* Prevent modal from being taller than viewport */
}
.modal-body {
    overflow-y: auto; /* Make only the body scrollable */
    padding: 0 1.5rem;
}
.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
}
.modal-header h2, .modal-header h3 { 
  margin: 0; 
  font-size: calc(1.15rem * var(--font-scale));
  font-weight: 600;
}
.close-btn {
    background: none;
    border: none;
    font-size: 2rem;
    line-height: 1;
    color: #6c757d;
    cursor: pointer;
}

.form-step {
  margin: 1rem 0;
  padding: 1rem;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: opacity 0.3s;
}
.form-step.disabled {
  opacity: 0.5;
  pointer-events: none;
  background-color: #f8f9fa;
}
.step-label {
  font-weight: 600;
  display: block;
  margin-bottom: 1rem;
  font-size: calc(1rem * var(--font-scale));
}
input[type="text"], input[type="date"], textarea, select {
  width: 100%;
  padding: 10px;
  font-size: calc(0.95rem * var(--font-scale));
  border-radius: 8px;
  border: 1px solid #ced4da;
  background-color: #f8f9fa;
  transition: border-color 0.2s, box-shadow 0.2s;
}
input:focus, textarea:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.search-wrapper {
    position: relative;
}
.spinner {
    position: absolute;
    right: 15px;
    top: 50%;
    transform: translateY(-50%);
    border: 3px solid #f3f3f3;
    border-top: 3px solid #007bff;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    animation: spin 1s linear infinite;
}
@keyframes spin {
  0% { transform: translateY(-50%) rotate(0deg); }
  100% { transform: translateY(-50%) rotate(360deg); }
}

.search-status {
  font-style: italic;
  color: #6c757d;
  margin-top: 1rem;
  text-align: center;
}
.search-results {
  list-style: none; padding: 0; margin: 10px 0 0 0; max-height: 120px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 8px;
}
.search-results li { padding: 10px; cursor: pointer; border-bottom: 1px solid #e9ecef; }
.search-results li:last-child { border-bottom: none; }
.search-results li:hover { background-color: #e9ecef; }

.create-new-btn {
  margin-top: 0.5rem;
  padding: 8px 16px;
  border: 1px solid #007bff;
  background: #e7f3ff;
  color: #007bff;
  border-radius: 50px;
  cursor: pointer;
  font-weight: 600;
}
.selected-medicine {
  background-color: #e7f3ff;
  border: 1px solid #007bff;
  padding: 12px;
  margin-top: 10px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.selected-medicine button { background: none; border: none; color: #007bff; cursor: pointer; text-decoration: underline; font-weight: 600; }

.date-picker {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}
.date-picker > div {
    flex: 1;
}
.date-picker label {
    font-weight: 500;
    font-size: calc(0.9rem * var(--font-scale));
    margin-bottom: 0.5rem;
}

.schedule-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1.5rem;
  text-align: center;
}
.meal-group h4 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-size: calc(0.95rem * var(--font-scale));
  font-weight: 600;
}
.custom-checkbox {
  font-weight: normal;
  display: block;
  cursor: pointer;
  margin-bottom: 0.5rem;
}

.modal-actions {
  display: flex; justify-content: flex-end; gap: 1rem; padding: 1rem 1.5rem;
  border-top: 1px solid #dee2e6;
  background-color: #f8f9fa;
}
.modal-btn-cancel, .modal-btn-confirm {
  padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: calc(0.95rem * var(--font-scale)); font-weight: 600;
}
.modal-btn-cancel { background-color: #6c757d; color: white; }
.modal-btn-confirm { background-color: #28a745; color: white; }
.modal-btn-confirm:disabled { background-color: #aaa; cursor: not-allowed; }

/* Nested request modal styles */
.request-modal-box {
  max-width: 450px;
}
.request-modal-box .modal-body {
    padding: 1rem 1.5rem;
}
.request-modal-box label {
    font-weight: 600;
    margin-top: 1rem;
}
.request-modal-box textarea {
    min-height: 100px;
    resize: vertical;
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
.custom-alert-box.info .alert-icon-wrapper { color: #007bff; }

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
.custom-alert-box.info .alert-btn { background-color: #007bff; }
</style>