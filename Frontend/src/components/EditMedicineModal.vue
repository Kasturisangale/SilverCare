<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Edit Medicine Schedule</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="input-group">
            <label>Dosage</label>
            <input type="text" v-model="localMed.dosage" placeholder="e.g., 1 pill, 10mg"/>
        </div>
        <div class="input-group">
            <label>End Date</label>
            <input type="date" v-model="localMed.endDate" />
        </div>

        <div class="schedule-grid">
          <div class="meal-group">
            <h4>Breakfast</h4>
            <label class="custom-checkbox"><input type="checkbox" v-model="localMed.breakfast_before" /> Before</label>
            <label class="custom-checkbox"><input type="checkbox" v-model="localMed.breakfast_after" /> After</label>
          </div>
          <div class="meal-group">
            <h4>Lunch</h4>
            <label class="custom-checkbox"><input type="checkbox" v-model="localMed.lunch_before" /> Before</label>
            <label class="custom-checkbox"><input type="checkbox" v-model="localMed.lunch_after" /> After</label>
          </div>
          <div class="meal-group">
            <h4>Dinner</h4>
            <label class="custom-checkbox"><input type="checkbox" v-model="localMed.dinner_before" /> Before</label>
            <label class="custom-checkbox"><input type="checkbox" v-model="localMed.dinner_after" /> After</label>
          </div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="modal-btn-cancel" @click="$emit('close')">Cancel</button>
        <button class="modal-btn-confirm" @click="update">Save Changes</button>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, watch } from 'vue';

export default {
  name: 'EditMedicineModal',
  props: {
    medicine: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'update-medication'],
  setup(props, { emit }) {
    const localMed = reactive({});

    watch(
      () => props.medicine,
      (newVal) => {
        if (newVal) Object.assign(localMed, newVal);
      },
      { immediate: true }
    );

    function update() {
      // The modal now only emits the data. The parent handles the API call.
      emit('update-medication', localMed);
    }

    return { localMed, update };
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
  background-color: rgba(0, 0, 0, 0.6); 
  display: flex; justify-content: center; align-items: center; 
  z-index: 2000;
  font-family: 'Inter', sans-serif;
}
.modal-content {
  background: white; padding: 0; border-radius: 12px; 
  width: 90%; max-width: 500px;
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
input[type="text"], input[type="date"] {
  width: 100%;
  padding: 12px;
  font-size: calc(1rem * var(--font-scale));
  border-radius: 8px;
  border: 1px solid #ced4da;
  background-color: #f8f9fa;
  transition: border-color 0.2s, box-shadow 0.2s;
}
input:focus {
  outline: none;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
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
.modal-btn-confirm { background-color: #007bff; color: white; }
</style>
