<template>
  <div class="dashboard-wrapper">
    <Navbar />
    <header class="dashboard-header">
      <h1>Member Details</h1>
      <p>Manage and view your dependents' profiles.</p>
    </header>

    <main class="main-content">
      <!-- Loading State -->
      <div v-if="isLoading" class="loading-state">Loading members...</div>

      <!-- Member Cards Grid -->
      <div v-else-if="filteredDependents.length > 0" class="members-grid">
        <div v-for="dep in filteredDependents" :key="dep.id" class="member-card">
          <div class="member-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22v-6M9 16H5l-1 4M15 16h4l1 4M12 6a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z"/><path d="M14 9.5c0 2-3 4.5-3 4.5s-3-2.5-3-4.5S9.33 5 11 5c1.2 0 3 1 3 4.5Z"/></svg>
          </div>
          <div class="member-info">
            <h3 class="member-name">{{ dep.firstName }} {{ dep.lastName }}</h3>
          </div>
          <div class="card-actions">
            <button class="action-btn view-btn" @click="viewProfile(dep)">View Profile</button>
            <button class="action-btn delete-btn" @click.stop="handleDelete(dep.id)">Delete</button>
          </div>
        </div>
      </div>

      <!-- No Dependents Message -->
      <div v-if="!isLoading && filteredDependents.length === 0" class="empty-state">
        <p>No members found. Please add one to get started.</p>
      </div>
      
      <!-- Add Member Button Container -->
      <div class="add-button-container">
        <button class="add-member-btn" @click="openAddModal">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          Add a Member
        </button>
      </div>
    </main>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeAddModal">
      <div class="modal-content">
        <div class="modal-header">
            <h3>Add a New Dependent</h3>
            <button class="close-btn" @click="closeAddModal">&times;</button>
        </div>
        <div class="modal-body">
            <p>Search for a user by name or username and select them to add.</p>
            <div class="search-container">
            <input type="text" v-model="searchQuery" placeholder="Enter username or name..." @input="handleSearch" />
            <div v-if="isSearching" class="spinner"></div>
            </div>
            <ul v-if="searchResults.length > 0" class="search-results">
            <li
                v-for="user in searchResults"
                :key="user.id"
                @click="selectUser(user)"
                :class="{ selected: selectedNewDependent && selectedNewDependent.id === user.id }"
            >
                {{ user.firstName }} {{ user.lastName }} ({{ user.username }})
            </li>
            </ul>
            <div v-if="searchAttempted && searchResults.length === 0 && !isSearching" class="no-results">
            No users found.
            </div>
        </div>
        <div class="modal-actions">
            <button class="modal-btn-cancel" @click="closeAddModal">Cancel</button>
            <button class="modal-btn-confirm" @click="handleAddDependent" :disabled="!selectedNewDependent">Request Dependent</button>
        </div>
      </div>
    </div>
    
    <!-- Confirm Delete Modal -->
    <ConfirmModal
      v-if="showDeleteModal"
      message="Are you sure you want to delete this member? This action cannot be undone."
      @confirm="deleteConfirmed"
      @cancel="showDeleteModal = false"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import Navbar from './Navbar.vue';
import ConfirmModal from './ConfirmModal.vue'; // Assuming you have this component
import apiService from '@/services/apiService';

const router = useRouter();
const dependents = ref([]);
const isLoading = ref(true);
const showAddModal = ref(false);
const showDeleteModal = ref(false);
const dependentToDelete = ref(null);

const searchQuery = ref('');
const searchResults = ref([]);
const selectedNewDependent = ref(null);
const isSearching = ref(false);
const searchAttempted = ref(false);

const filteredDependents = computed(() =>
  dependents.value.filter(dep => dep.role === 'senior_citizen')
);

async function fetchDependents() {
  isLoading.value = true;
  try {
    const res = await apiService.get('/sc/my-dependents');
    dependents.value = Array.isArray(res.data.dependents) ? res.data.dependents : [];
  } catch (err) {
    console.error('Error fetching dependents:', err);
    dependents.value = [];
  } finally {
    isLoading.value = false;
  }
}

async function apiAddDependent(userToAdd) {
  try {
    const res = await apiService.post('/sc/request-senior', { senior_id: userToAdd.id });
    return res.data;
  } catch (err) {
    console.error('Error adding dependent:', err.message);
    return { success: false, message: err.message };
  }
}

async function apiDeleteDependent(seniorId) {
  try {
    await apiService.delete('/sc/delete-dependent', { data: { senior_id: seniorId } });
  } catch (err) {
    console.error('Error deleting dependent:', err.message);
  }
}

async function searchAllUsers(query) {
  if (!query) return [];
  try {
    const res = await apiService.get(`/sc/search-users?query=${encodeURIComponent(query)}`);
    return res.data.users;
  } catch (err) {
    console.error('Error searching users:', err.response?.data || err.message);
    return [];
  }
}

onMounted(fetchDependents);

function viewProfile(dependent) {
  router.push({ name: 'DependentProfile', params: { userId: dependent.id } });
}

function handleDelete(userId) {
  dependentToDelete.value = userId;
  showDeleteModal.value = true;
}

async function deleteConfirmed() {
    if (dependentToDelete.value) {
        await apiDeleteDependent(dependentToDelete.value);
        await fetchDependents();
    }
    showDeleteModal.value = false;
    dependentToDelete.value = null;
}

function openAddModal() {
  showAddModal.value = true;
}

function closeAddModal() {
  showAddModal.value = false;
  searchQuery.value = '';
  searchResults.value = [];
  selectedNewDependent.value = null;
  isSearching.value = false;
  searchAttempted.value = false;
}

let searchTimeout;
function handleSearch() {
  clearTimeout(searchTimeout);
  isSearching.value = true;
  searchAttempted.value = true;
  searchTimeout = setTimeout(async () => {
    searchResults.value = await searchAllUsers(searchQuery.value);
    isSearching.value = false;
  }, 300);
}

function selectUser(user) {
  selectedNewDependent.value = user;
}

async function handleAddDependent() {
  if (!selectedNewDependent.value) return;
  const response = await apiAddDependent(selectedNewDependent.value);
  if (response.success) {
    closeAddModal();
    await fetchDependents();
  } else {
    alert(response.message || 'Failed to add dependent.');
    closeAddModal();
  }
}
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
  text-align: center;
  margin-bottom: 2.5rem;
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

.add-button-container {
    display: flex;
    justify-content: center;
    margin-top: 2.5rem;
    padding-top: 2.5rem;
    border-top: 1px solid #e9ecef;
}

.add-member-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 0.8rem 1.8rem;
  font-size: calc(1rem * var(--font-scale));
  font-weight: 600;
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(40, 167, 69, 0.3);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.add-member-btn:hover {
  background-color: #218838;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
}

.main-content {
  background-color: #ffffff;
  border-radius: 16px;
  padding: 2.5rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem;
  color: #6c757d;
  font-size: 1.2rem;
  font-style: italic;
}

.members-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 2rem;
}

.member-card {
  border-radius: 16px;
  padding: 2rem 1.5rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  border: 1px solid #e9ecef;
  background-color: #e7f5ff; /* New card color */
}
.member-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 28px rgba(0,0,0,0.1);
}

.member-icon {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1.5rem;
  color: #0056b3;
  background-color: #ffffff;
  border: 2px solid #b3d7ff;
}

.member-info {
    margin-bottom: 1.5rem;
}
.member-name {
  font-size: 1.5rem;
  font-weight: 600;
  font-family: 'Georgia', serif;
  color: #343a40;
}
.member-username {
    color: #6c757d;
    font-size: 1rem;
}

.card-actions {
    display: flex;
    gap: 1rem;
    width: 100%;
    margin-top: auto; /* Pushes actions to the bottom */
}
.action-btn {
    flex: 1;
    padding: 0.7rem;
    border-radius: 8px;
    border: 1px solid;
    background: transparent;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
}
.view-btn {
    border-color: #007bff;
    color: #007bff;
}
.view-btn:hover {
    background-color: #007bff;
    color: white;
}
.delete-btn {
    border-color: #dc3545;
    color: #dc3545;
}
.delete-btn:hover {
    background-color: #dc3545;
    color: white;
}

/* Modal styles */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background-color: rgba(0, 0, 0, 0.6); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-content { background: white; padding: 0; border-radius: 12px; width: 90%; max-width: 500px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 1rem 1.5rem; background-color: #f8f9fa; border-bottom: 1px solid #dee2e6; }
.modal-header h3 { margin: 0; font-size: 1.25rem; font-weight: 600; }
.close-btn { background: none; border: none; font-size: 2rem; line-height: 1; color: #6c757d; cursor: pointer; }
.modal-body { padding: 1.5rem; }
.modal-body p { margin-top: 0; color: #6c757d; }
.search-container input { width: 100%; padding: 12px; font-size: 1rem; border: 1px solid #ced4da; border-radius: 8px; }
.search-results { list-style: none; padding: 0; margin: 1rem 0 0 0; max-height: 200px; overflow-y: auto; border: 1px solid #dee2e6; border-radius: 8px; }
.search-results li { padding: 12px; cursor: pointer; border-bottom: 1px solid #e9ecef; }
.search-results li:last-child { border-bottom: none; }
.search-results li:hover { background-color: #e9ecef; }
.search-results li.selected { background-color: #007bff; color: white; }
.no-results { padding: 1rem; color: #6c757d; text-align: center; }
.modal-actions { display: flex; justify-content: flex-end; gap: 1rem; padding: 1rem 1.5rem; border-top: 1px solid #dee2e6; background-color: #f8f9fa; }
.modal-btn-cancel, .modal-btn-confirm { padding: 10px 20px; border: none; border-radius: 8px; cursor: pointer; font-size: 0.95rem; font-weight: 600; }
.modal-btn-cancel { background-color: #6c757d; color: white; }
.modal-btn-confirm { background-color: #28a745; color: white; }
.modal-btn-confirm:disabled { background-color: #aaa; cursor: not-allowed; }
</style>
