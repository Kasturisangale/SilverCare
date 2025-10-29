<!-- components/ConfirmModal.vue -->
<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal-box">
      <h3>Confirm Deletion</h3>
      <p>{{ message }}</p>
      <div class="modal-actions">
        <button @click="handleCancel">Cancel</button>
        <button class="danger" @click="handleConfirm">Yes, delete</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineEmits} from 'vue'

const emit = defineEmits(['confirm', 'cancel'])

// const props = defineProps({
//   message: {
//     type: String,
//     default: "Are you sure you want to delete this item?"
//   }
// })

function handleClose() {
  emit('cancel')
}

function handleCancel() {
  emit('cancel')
}

function handleConfirm() {
  emit('confirm')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  justify-content: center;
  align-items: center;
}
.modal-box {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 6px 16px rgba(0,0,0,0.2);
  max-width: 400px;
  width: 90%;
  text-align: center;
}
.modal-actions {
  display: flex;
  justify-content: space-around;
  margin-top: 1.5rem;
}
button {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  font-weight: bold;
  cursor: pointer;
}
button.danger {
  background-color: #e74c3c;
  color: white;
}
button:not(.danger) {
  background-color: #ccc;
  color: white;
}
</style>
