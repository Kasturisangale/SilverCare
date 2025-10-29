<!-- eslint-disable vue/multi-word-component-names -->
<template>
  <div>
    <nav class="app-navbar">
      <div class="navbar-container">
        <!-- Brand/Logo -->
        <a class="navbar-brand" :href="homeLink">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="brand-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
          <span>SilverCare</span>
        </a>

        <!-- Navbar Actions (Icons) -->
        <div class="nav-actions" v-if="role">
          <!-- Health Entry -->
          <div v-if="role === 'senior_citizen' || role === 'care_giver'">
            <div class="nav-action-item" @click="showHealthEntryModal = true" title="Add Health Entry">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>
            </div>
          </div>

          <!-- Notifications -->
           <div v-if="role === 'senior_citizen' || role === 'care_giver'">
            <div class="nav-action-item" @click="toggleModal" title="Notifications">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
              <span v-if="notificationCount > 0" class="notification-badge">
                {{ notificationCount }}
              </span>
            </div>
          </div>

          <!-- Profile Dropdown -->
          <div class="nav-action-item dropdown-container" title="Profile">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            
            <div class="dropdown-menu-hover">
              <a class="dropdown-item" :href="homeLink">Home</a>
              <template v-if="role === 'senior_citizen' || role === 'care_giver'">
                <a class="dropdown-item" href="/profile">My Profile</a>
                <a class="dropdown-item" href="/stats">Reports</a>
              </template>
              <a v-if="role==='care_giver'" class="dropdown-item" href="/manage-dependents">Member Details</a>
              <template v-if="role==='admin'">
                <a class="dropdown-item" href="/admin-medicines">Medicines</a>
              </template>
              <div class="dropdown-divider"></div>
              <a class="dropdown-item logout-item" @click="logout">Logout</a>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <HealthEntry
      v-if="showHealthEntryModal"
      :role="role"
      @close="showHealthEntryModal = false"
    />
    <NotificationModal
      :show="showModal"
      :role="role"
      @close="showModal = false"
      @updated="getNotificationCount"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed} from 'vue'
import { useRouter } from 'vue-router'
import NotificationModal from "@/components/NotificationModal.vue"
import HealthEntry from "@/components/HealthEntry.vue"
import apiService from '@/services/apiService'

const role = ref(null)
const router = useRouter()
const showModal = ref(false)
const notificationCount = ref(0)
const showHealthEntryModal = ref(false)

const homeLink = computed(() => {
  if (role.value === 'care_giver') return '/cg';
  if (role.value === 'senior_citizen') return '/sc';
  if (role.value === 'admin') return '/admin';
  return '/';
});

onMounted(() => {
  const storedRole = sessionStorage.getItem('role')
  if (storedRole) {
    role.value = storedRole
    getNotificationCount()
  }
})

function toggleModal() {
  showModal.value = true
}

async function getNotificationCount() {
  try {
    const res = await apiService.get("/sc/notifications");
    notificationCount.value = res.data?.count || 0;
  } catch (err) {
    console.error("Error fetching notifications:", err);
  }
}

function logout() {
  sessionStorage.clear()
  // Clean up global style on logout
  document.body.style.removeProperty('--font-scale');
  router.push('/login')
}
</script>

<style scoped>
/* --- Global styles for accessibility --- */
:global(body) {
  /* Set a default value for the font-scale variable */
  --font-scale: 1;
}


.app-navbar {
  background-color: #ffffff;
  padding: 0.75rem 2rem;
  font-family: 'Inter', sans-serif;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1030;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  max-width: 1400px; /* Or your preferred max-width */
  margin: 0 auto;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #343a40 !important;
  font-size: calc(1.5rem * var(--font-scale));
  font-weight: 600;
  text-decoration: none;
  transition: font-size 0.3s ease;
}

.brand-icon {
  color: #007bff;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-action-item {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: #495057;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.nav-action-item:hover {
  background-color: #f1f3f5;
  color: #007bff;
}


.notification-badge {
  position: absolute;
  top: 4px;
  right: 4px;
  background-color: #dc3545;
  color: white;
  font-size: 10px;
  font-weight: 600;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  border: 1px solid white;
}

.dropdown-container {
  position: relative;
}

.dropdown-menu-hover {
  position: absolute;
  top: 120%; /* Position below the icon */
  right: 0;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  width: 180px;
  padding: 0.5rem 0;
  z-index: 1000;
  border: 1px solid #e9ecef;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.25s ease-out;
}

.dropdown-container:hover .dropdown-menu-hover {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-menu-hover .dropdown-item {
  display: block;
  padding: 0.6rem 1rem;
  font-size: calc(0.95rem * var(--font-scale));
  color: #333 !important;
  font-weight: 500;
  text-decoration: none;
  transition: background-color 0.2s ease, font-size 0.3s ease;
}

.dropdown-menu-hover .dropdown-item:hover {
  background-color: #f8f9fa;
  color: #007bff !important;
}

.dropdown-divider {
  height: 1px;
  background-color: #e9ecef;
  margin: 0.5rem 0;
}

.logout-item {
  color: #d9534f !important;
  font-weight: bold !important;
}

/* Modal styles from original file, kept for functionality */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-content {
  background-color: white;
  padding: 2rem;
  border-radius: 10px;
  width: 100px;
  max-width: 30%;
  z-index: 1060;
}
</style>
