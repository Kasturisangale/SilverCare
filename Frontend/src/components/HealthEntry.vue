<template>
  <div class="modal-overlay" @click.self="emitClose">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Health Entry</h3>
        <button class="close-btn" @click="emitClose">&times;</button>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="submitHealthEntry">
          <div v-if="role === 'care_giver'" class="input-group">
            <label for="senior-select">Select Senior Citizen</label>
            <select id="senior-select" v-model="selectedSenior" class="form-control">
              <option disabled :value="null">-- Select a dependent --</option>
              <option v-for="senior in seniors" :key="senior.id" :value="senior">
                {{ senior.username }}
              </option>
            </select>
          </div>
          
          <div class="form-row">
            <div class="input-group">
              <label for="bp_systolic">BP Systolic</label>
              <div class="input-with-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                <input id="bp_systolic" type="number" v-model.number="healthData.bp_systolic" placeholder="e.g., 120" required />
              </div>
            </div>
            <div class="input-group">
              <label for="bp_diastolic">BP Diastolic</label>
               <div class="input-with-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                <input id="bp_diastolic" type="number" v-model.number="healthData.bp_diastolic" placeholder="e.g., 80" required />
              </div>
            </div>
          </div>
          
          <div class="input-group">
            <label for="sugar_level">Sugar Level (mg/dL)</label>
            <div class="input-with-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"></path></svg>
                <input id="sugar_level" type="number" step="0.1" v-model.number="healthData.sugar_level" placeholder="e.g., 95.5" required />
            </div>
          </div>
        </form>
      </div>
      <div class="modal-actions">
        <button type="button" class="modal-btn-cancel" @click="emitClose">Cancel</button>
        <button type="submit" class="modal-btn-confirm" @click="submitHealthEntry" :disabled="!isFormValid">Submit</button>
      </div>
    </div>

    <!-- Custom Alert Modal -->
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
import { ref, computed, defineEmits, defineProps, watch } from 'vue'
import apiService from '@/services/apiService'

const props = defineProps({
  role: String,
})

const healthData = ref({
  bp_systolic: '',
  bp_diastolic: '',
  sugar_level: ''
})
const selectedSenior = ref(null)
const seniors = ref([])

// --- Custom Alert State ---
const alertMessage = ref('');
const alertType = ref('info');

const isFormValid = computed(() =>
  healthData.value.bp_systolic &&
  healthData.value.bp_diastolic &&
  healthData.value.sugar_level &&
  (props.role !== 'care_giver' || selectedSenior.value)
)

watch(() => props.role, (role) => {
  if (role === 'care_giver') {
    fetchDependents()
  }
}, { immediate: true })

const emit = defineEmits(['close'])
function emitClose() {
  emit('close')
}

function showAlert(message, type = 'error') {
  alertMessage.value = message;
  alertType.value = type;
}

async function fetchDependents() {
  try {
    const res = await apiService.get('/sc/my-dependents');
    seniors.value = Array.isArray(res.data.dependents) ? res.data.dependents : [];
  } catch (err) {
    seniors.value = []
    showAlert('Could not fetch dependents list.', 'error');
  }
}

async function submitHealthEntry() {
  if (!isFormValid.value) {
    showAlert("Please fill in all the fields.", 'error');
    return;
  }

  if (
    Number(healthData.value.bp_systolic) <= 0 ||
    Number(healthData.value.bp_diastolic) <= 0 ||
    Number(healthData.value.sugar_level) <= 0
  ) {
    showAlert("Please enter correct readings (values must be greater than 0).", 'error');
    return;
  }
  if (props.role === 'care_giver' && !selectedSenior.value) {
    showAlert("Please select a senior citizen first.", 'error')
    return
  }
  try {
    const data = {
      ...healthData.value,
      senior_id: props.role === 'care_giver' ? selectedSenior.value.id : undefined
    }
    const res = await apiService.post("/sc/health-entry", data)
    if (res.status === 201) {
      showAlert(res.data.message, 'success')
      healthData.value = { bp_systolic: '', bp_diastolic: '', sugar_level: '' }
      setTimeout(() => {
        alertMessage.value = '';
        emitClose();
      }, 2000);
    } else {
      showAlert(res.data.error || 'An error occurred.', 'error')
    }
  } catch (error) {
    if (error.response) {
      showAlert(error.response.data.error || "Invalid input", 'error')
    } else {
      showAlert('An unexpected error occurred.', 'error');
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
  background-color: rgba(0, 0, 0, 0.6); 
  display: flex; justify-content: center; align-items: center; 
  z-index: 1050;
  font-family: 'Inter', sans-serif;
}
.modal-content {
  background: white; padding: 0; border-radius: 12px; 
  width: 90%; max-width: 480px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  overflow: hidden;
}
.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
}
.modal-header h3 { 
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
.modal-body {
    padding: 1.5rem;
}

.input-group {
  margin-bottom: 1.25rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: calc(0.9rem * var(--font-scale));
}
.input-with-icon {
  position: relative;
}
.input-with-icon svg {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #adb5bd;
}
input, select {
  width: 100%;
  padding: 12px;
  font-size: calc(1rem * var(--font-scale));
  border-radius: 8px;
  border: 1px solid #ced4da;
  background-color: #f8f9fa;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-with-icon input {
    padding-left: 2.5rem;
}
input:focus, select:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-row {
  display: flex;
  gap: 1rem;
}
.form-row .input-group {
  flex: 1;
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
