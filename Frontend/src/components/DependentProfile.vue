<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <Navbar />
    </header>

    <main class="main-content">
      <div v-if="isLoading" class="loading-state">Loading Profile...</div>
      <div v-else-if="!dependent" class="loading-state">Profile not found.</div>

      <div v-else class="profile-container">
        <div class="profile-header">
            <h1 class="profile-title">{{ dependent.firstName }}'s Profile</h1>
        </div>

        <!-- User Details -->
        <div class="profile-details">
            <div class="info-row">
                <span class="label">Full Name</span>
                <span class="value">{{ dependent.firstName }} {{ dependent.lastName }}</span>
            </div>
        </div>

        <!-- Daytime Meds -->
        <div class="meds-section">
          <div class="meds-header">
            <div class="meds-header-title">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
              <h3>Daytime Meds</h3>
            </div>
            <button class="add-medicine-btn" @click="openAddMedModal">Add Medicine</button>
          </div>
          <div v-if="daytimeMeds.length === 0" class="no-meds">No daytime medicines scheduled.</div>
          <div v-else class="med-list">
            <div v-for="med in daytimeMeds" :key="med.id" class="med-card daytime">
              <div class="med-name-wrapper">
                <svg class="med-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="5" width="10" height="14" rx="2" ry="2"></rect><path d="M9 5V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"></path><line x1="10" y1="12" x2="14" y2="12"></line><line x1="12" y1="10" x2="12" y2="14"></line></svg>
                <span class="med-name">{{ med.medicineTitle }}</span>
              </div>
              <span class="med-dosage">{{ med.dosage }}</span>
              <span class="med-time">{{ formatTime(med) }}</span>
              <div class="med-controls">
                <button class="icon-btn edit-btn" @click="openEditModal(med)" title="Edit"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>
                <button class="icon-btn delete-btn" @click="openDeleteModal(med.id)" title="Delete"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg></button>
              </div>
            </div>
          </div>
        </div>

        <!-- Nighttime Meds -->
        <div class="meds-section">
          <div class="meds-header">
             <div class="meds-header-title">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
                <h3>Nighttime Meds</h3>
             </div>
          </div>
          <div v-if="nighttimeMeds.length === 0" class="no-meds">No nighttime medicines scheduled.</div>
          <div v-else class="med-list">
            <div v-for="med in nighttimeMeds" :key="med.id" class="med-card nighttime">
                <div class="med-name-wrapper">
                  <svg class="med-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="5" width="10" height="14" rx="2" ry="2"></rect><path d="M9 5V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1"></path><line x1="10" y1="12" x2="14" y2="12"></line><line x1="12" y1="10" x2="12" y2="14"></line></svg>
                  <span class="med-name">{{ med.medicineTitle }}</span>
                </div>
                <span class="med-dosage">{{ med.dosage }}</span>
                <span class="med-time">{{ formatTime(med) }}</span>
                <div class="med-controls">
                    <button class="icon-btn edit-btn" @click="openEditModal(med)" title="Edit"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg></button>
                    <button class="icon-btn delete-btn" @click="openDeleteModal(med.id)" title="Delete"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg></button>
                </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Modals -->
    <AddMedicineModal
      v-if="showAddMedModal"
      @close="closeAddMedModal"
      @add-medication="handleAddMedication"
    />
    <EditMedicineModal
      v-if="showEditMedModal"
      :medicine="medToEdit"
      @close="closeEditMedModal"
      @update-medication="handleUpdateMedication"
    />
    <ConfirmModal
      v-if="showDeleteModal"
      message="Are you sure you want to delete this medication from the schedule?"
      @confirm="handleDeleteConfirmed"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>


<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AddMedicineModal from './AddMedicineModal.vue'
import ConfirmModal from './ConfirmModal.vue'
import EditMedicineModal from './EditMedicineModal.vue'
import Navbar from './Navbar.vue'
import apiService from '@/services/apiService'

const route = useRoute()
let userId = route.params.userId

if (!userId) {
  userId = sessionStorage.getItem('user_id') || null
}

const isLoading = ref(true)
const dependent = ref(null)
const medications = ref([])
const showAddMedModal = ref(false)
const showDeleteModal = ref(false)
const medToDelete = ref(null)
const showEditMedModal = ref(false)
const medToEdit = ref(null)

const daytimeMeds = computed(() =>
  medications.value.filter(
    med =>
      med.breakfast_before ||
      med.breakfast_after ||
      med.lunch_before ||
      med.lunch_after
  )
)

const nighttimeMeds = computed(() =>
  medications.value.filter(
    med => med.dinner_before || med.dinner_after
  )
)

const formatTime = (med) => {
  const slots = []
  if (med.breakfast_before) slots.push('Before Breakfast')
  if (med.breakfast_after) slots.push('After Breakfast')
  if (med.lunch_before) slots.push('Before Lunch')
  if (med.lunch_after) slots.push('After Lunch')
  if (med.dinner_before) slots.push('Before Dinner')
  if (med.dinner_after) slots.push('After Dinner')
  return slots.join(', ')
}

function openEditModal(med) {
  medToEdit.value = { ...med }
  showEditMedModal.value = true
}

function closeEditMedModal() {
  showEditMedModal.value = false
  medToEdit.value = null
}

async function handleUpdateMedication(updatedData) {
  try {
    const res = await apiService.put(`/sc/medication/${medToEdit.value.id}`, updatedData)
    if (res.status === 200) {
      alert('Medication updated successfully.')
      closeEditMedModal()
    }
  } catch (err) {
    console.error('Error updating medication:', err)
    const backendMsg = err.response?.data?.error || err.response?.data?.message || err.message
    alert(backendMsg)
  }
}

async function getDependentDetails(id) {
  try {
    const res = await apiService.get(`/sc/dependent/${id}/details`)
    return res.data
  } catch (err) {
    console.error('Error fetching dependent details:', err)
    return null
  }
}

async function getDependentMedications(id) {
  try {
    const res = await apiService.get(`/sc/dependent/${id}/medications`)
    return res.data.medications || []
  } catch (err) {
    console.error('Error fetching medications:', err)
    return []
  }
}

async function deleteMedicationMapping(medId) {
  try {
    const res = await apiService.delete(`/sc/medication/${medId}`)
    return res.data
  } catch (err) {
    console.error('Error deleting medication:', err)
    return { success: false }
  }
}
async function addMedicationToDependent(userId, payload) {
  try {
    const userRole = sessionStorage.getItem('role');
    const requestBody = { ...payload };
    if (userRole === 'care_giver') {
      requestBody.senior_citizen_id = Number(userId);
    }

    const res = await apiService.post(`/sc/assign-medicine`, requestBody);

    console.log('🔍 API Response:', res.data);

    // Debug check: log what you're actually testing
    if (res.data && res.data.medication) {
      console.log('✅ Medication found:', res.data.medication);
      return {
        success: true,
        medication: res.data.medication,
        message: res.data.message || 'Medicine assigned successfully.'
      };
    } else {
      console.warn('⚠️ Medication not found in response');
      return {
        success: false,
        message: res.data.message || 'Failed to assign medicine.'
      };
    }

  } catch (err) {
    console.error('❌ Error adding medication:', err.response?.data || err.message);
    return {
      success: false,
      message: err.response?.data?.error || 'Failed to assign medicine.'
    };
  }
}


function openAddMedModal() {
  showAddMedModal.value = true
}

function closeAddMedModal() {
  showAddMedModal.value = false
}

function openDeleteModal(medId) {
  medToDelete.value = medId
  showDeleteModal.value = true
}

async function handleDeleteConfirmed() {
  if (!medToDelete.value) return

  const result = await deleteMedicationMapping(medToDelete.value)
  if (result.success || result.message) {
    medications.value = medications.value.filter(m => m.id !== medToDelete.value)
  } else {
    alert('Failed to delete medication.')
  }

  showDeleteModal.value = false
  medToDelete.value = null
}

async function handleAddMedication(payload) {
  const response = await addMedicationToDependent(userId, payload);

  if (response.success) {
    alert(response.message);  // shows: "Medicine assigned and status tracking initialized."
    closeAddMedModal();
    console.log('New medication added:', response.medication);  // contains `medicine_id`, `medicineTitle`, etc.
    medications.value.push(response.medication);
  } else {
    alert(response.message);
  }
}
onMounted(async () => {
  if (!userId) {
    console.warn("No userId found for profile");
    isLoading.value = false;
    return;
  }
  const [details, meds] = await Promise.all([
    getDependentDetails(userId),
    getDependentMedications(userId),
  ])
  dependent.value = details
  medications.value = meds
  isLoading.value = false
})
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

.main-content {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.loading-state {
    color: white;
    font-size: 1.5rem;
    text-align: center;
    margin-top: 5rem;
}

.profile-container {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 2.5rem;
  width: 100%;
  max-width: 950px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.profile-header {
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 1.5rem;
    margin-bottom: 1.5rem;
}

.profile-title {
  font-family: 'Georgia', serif;
  font-size: calc(2.5rem * var(--font-scale));
  font-weight: 700;
  color: #343a40;
  margin: 0;
}

.profile-details {
  padding-top: 1rem;
  margin-bottom: 2rem;
}

.info-row {
  display: grid;
  grid-template-columns: 150px 1fr;
  align-items: center;
  gap: 1.5rem;
  padding: 0.8rem 0; /* Reduced padding */
  border-bottom: 1px solid #e9ecef;
}
.info-row:last-child {
    border-bottom: none;
}

.label {
  font-weight: 600;
  font-size: calc(1rem * var(--font-scale)); /* Reduced font size */
  color: #6c757d;
}

.value {
  font-size: calc(1rem * var(--font-scale)); /* Reduced font size */
  color: #212529;
  font-weight: 500;
  text-align: left;
}

.meds-section {
  margin-bottom: 2rem;
}

.meds-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}
.meds-header-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: #343a40;
}
.meds-header-title h3 {
    font-family: 'Georgia', serif;
    font-size: calc(1.8rem * var(--font-scale));
    margin: 0;
}
.meds-header-title svg {
    color: #007bff;
}

.add-medicine-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 0.7rem 1.5rem;
  font-size: calc(0.95rem * var(--font-scale));
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,123,255,0.25);
  transition: all 0.2s ease;
  font-weight: 600;
}
.add-medicine-btn:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,123,255,0.3);
}

.med-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.med-card {
  display: grid;
  grid-template-columns: 2.5fr 1.5fr 2fr auto;
  align-items: center;
  gap: 1rem;
  padding: 0.8rem 1.2rem;
  border-radius: 12px;
  border: 1px solid #dee2e6;
}
.med-card.daytime { background-color: #fff9e6; }
.med-card.nighttime { background-color: #f3e8fd; }

.med-name-wrapper {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.med-icon {
    color: #495057;
}

.med-name {
  font-weight: 600;
  font-size: calc(1rem * var(--font-scale));
}
.med-dosage {
  font-size: calc(0.95rem * var(--font-scale));
  color: #6c757d;
}
.med-time {
  font-size: calc(0.95rem * var(--font-scale));
  color: #495057;
}

.med-controls {
  display: flex;
  gap: 0.75rem;
}
.icon-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}
.icon-btn.edit-btn { color: #007bff; }
.icon-btn.delete-btn { color: #dc3545; }
.icon-btn:hover { background-color: #e9ecef; }

.no-meds {
  padding: 1.5rem;
  text-align: center;
  color: #6c757d;
  font-style: italic;
  background-color: #f8f9fa;
  border-radius: 12px;
}
</style>