<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <Navbar />
    </header>

    <main class="main-content">
      <div class="profile-container">
        <div class="profile-header">
            <h1 class="profile-title">My Profile</h1>
            <button v-if="user.role==='senior_citizen'"
                class="view-profile-btn" 
                @click="goToMyProfilePage">
                View Full Medical Profile
            </button>
        </div>
        
        <div class="profile-details">
          <div class="info-row">
            <span class="label">Full Name</span>
            <span class="value">{{ user.firstName }} {{ user.lastName }}</span>
          </div>
          <div class="info-row">
            <span class="label">Username</span>
            <span class="value">{{ user.username }}</span>
          </div>
          
          <!-- Caregiver Information -->
          <div v-if="user.role === 'senior_citizen' && caregiver">
            <h3 class="section-title">My Caregiver</h3>
            <div class="info-row">
              <span class="label">Full Name</span>
              <span class="value">{{ caregiver.firstName }} {{ caregiver.lastName }}</span>
            </div>
            <div class="info-row">
              <span class="label">Username</span>
              <span class="value">{{ caregiver.username }}</span>
            </div>
          </div>
          <div v-else-if="user.role === 'senior_citizen' && !caregiver" class="no-data-notice">
            <h3 class="section-title">My Caregiver</h3>
            <p>No caregiver has been assigned yet.</p>
          </div>
          
          <!-- Dependents Information -->
          <div v-if="user.role === 'care_giver' && dependents.length > 0">
            <h3 class="section-title">My Dependents</h3>
            <div v-for="(d, index) in dependents" :key="d.id" class="dependent-section">
              <h4 class="dependent-title">Dependent {{ index + 1 }}</h4>
              <div class="info-row">
                <span class="label">Full Name</span>
                <span class="value">{{ d.firstName }} {{ d.lastName }}</span>
              </div>
              <div class="info-row">
                <span class="label">Username</span>
                <span class="value">{{ d.username }}</span>
              </div>
            </div>
          </div>
           <div v-else-if="user.role === 'care_giver' && dependents.length === 0" class="no-data-notice">
            <h3 class="section-title">My Dependents</h3>
            <p>You have not added any dependents yet.</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Navbar from './Navbar.vue'
import { useRouter } from 'vue-router'
import {jwtDecode} from 'jwt-decode'
import { fetchMyMedicines, fetchMyCaregiver, fetchMyDependents } from '@/services/profileService'

const user = ref({})
const caregiver = ref(null)
const dependents = ref([])
const medicines = ref([])

const userId = sessionStorage.getItem('user_id')
const role = sessionStorage.getItem('role')
const router = useRouter()

function goToMyProfilePage() {
  const myUserId = sessionStorage.getItem('user_id'); 
  if (myUserId) {
    router.push(`/cg/${myUserId}/dependantProfile`);
  } else {
    alert("User ID not found in session.");
  }
}

onMounted(async () => {
  if (!userId || !role) {
    router.push('/login');
    return;
  }

  const token = sessionStorage.getItem('accesstoken');
  if (token) {
    const decoded = jwtDecode(token);
    user.value = {
      id: decoded.id,
      firstName: decoded.first_name,
      lastName: decoded.last_name,
      username: decoded.username,
      role
    };
  }

  if (role === 'senior_citizen') {
    medicines.value = await fetchMyMedicines();
    caregiver.value = await fetchMyCaregiver();
  }

  if (role === 'care_giver') {
    dependents.value = await fetchMyDependents();
  }
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

.main-content {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.profile-container {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 2.5rem;
  width: 100%;
  max-width: 800px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.profile-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
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
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 0;
  border-bottom: 1px solid #e9ecef;
}
.info-row:last-child {
    border-bottom: none;
}

.label {
  font-weight: 600;
  font-size: calc(1.1rem * var(--font-scale));
  color: #6c757d;
}

.value {
  font-size: calc(1.1rem * var(--font-scale));
  color: #212529;
  font-weight: 500;
  text-align: right;
}

.section-title {
  font-family: 'Georgia', serif;
  font-size: calc(1.8rem * var(--font-scale));
  margin: 2.5rem 0 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
  color: #343a40;
}

.dependent-section {
  padding: 1.5rem;
  margin-bottom: 1rem;
  border-radius: 12px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
}

.dependent-title {
  font-size: calc(1.25rem * var(--font-scale));
  font-weight: 600;
  margin-bottom: 1rem;
  color: #495057;
}

.view-profile-btn {
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
.view-profile-btn:hover {
  background-color: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,123,255,0.3);
}

.no-data-notice {
    padding: 1rem;
    text-align: center;
    font-style: italic;
    color: #6c757d;
}
</style>
