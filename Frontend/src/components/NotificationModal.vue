<template>
  <div v-if="show" class="modal-backdrop" @click.self="close">
    <div class="modal-content">
      <h2>Notifications</h2>

      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="requests.length === 0" class="no-requests">No notifications</div>

      <div v-else class="requests-list">
        <div
          class="request-card"
          v-for="(req, index) in requests"
          :key="index"
        >
          <template v-if="req.type === 'caregiver_request'">
            <p>
              You have a new caregiver request from
              <strong>{{ req.caregiver_username }}</strong>
            </p>
            <div class="buttons">
              <button
                class="btn-approve"
                @click="respondToRequest(req.caregiver_id, true)"
              >
                Approve
              </button>
              <button
                class="btn-reject"
                @click="respondToRequest(req.caregiver_id, false)"
              >
                Reject
              </button>
            </div>
          </template>

          <template v-else-if="req.type === 'poke'">
            <p>💊 Reminder from {{ req.from }}: Take medicine {{req.medicine_title}} ({{ req.slot }}).
                  <span class="close-icon" @click="dismissNotification(index)">×</span>
            </p>
          </template>

          <template v-else-if="req.type === 'sos'">
            <p>🚨 SOS Alert! {{req.from}} needs immediate assistance!
                  <span class="close-icon" @click="dismissNotification(index)">×</span>
            </p>
          </template>
        </div>
      </div>

      <!-- Close button outside the loop -->
      <button class="close-btn" @click="close">Close</button>
    </div>
  </div>
</template>

<script>
import apiService from '@/services/apiService';
export default {
  name: "NotificationModal",
  props: {
    show: Boolean,
    role:String
  },
  emits: ['close', 'updated'],
  data() {
    return {
      requests: [],
      loading: true,
    };
  },
  methods: {
    close() {
      this.$emit("close");
    },
    async fetchRequests() {
  this.loading = true;
  try {
    const res = await apiService.get("/sc/notifications");
    this.requests = res.data?.notifications || [];
  } catch (error) {
    console.error("Failed to fetch notifications:", error);
  } finally {
    this.loading = false;
  }
},async dismissNotification(index) {
  const notif = this.requests[index];
  if (notif.id) { // only mark read if it came from Notification table
    try {
      await apiService.put(`/sc/notifications/${notif.id}/read`);
    } catch (err) {
      console.error("Error marking notification as read:", err);
    }
  }
  this.requests.splice(index, 1);
  this.$emit('updated');
},
    async respondToRequest(caregiver_id, approve) {
      try {
        await apiService.post("/sc/approve-caregiver", {
          caregiver_id,
          approve,
        });
        this.requests = this.requests.filter((r) => r.caregiver_id !== caregiver_id);
        this.$emit("updated");
      } catch (error) {
        console.error("Approval error:", error);
      }
    },
  },
  watch: {
    show(newVal) {
      if (newVal) this.fetchRequests();
    },
  },
};
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 400px;
  max-height: 80vh;
  overflow-y: auto;
}
.request-card {
  border: 1px solid #ccc;
  padding: 12px;
  margin-bottom: 10px;
  border-radius: 6px;
  text-align: left;
}
.buttons {
  display: flex;
  gap: 10px;
  margin-top: 8px;
}
.close-btn {
  margin-top: 20px;
  background: #666;
  color: white;
  padding: 6px 12px;
  border: none;
  cursor: pointer;
}
.loading, .no-requests {
  text-align: center;
  padding: 20px;
  color: #555;
}
.btn-approve {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
}

.btn-reject {
  background-color: #e53935;
  color: white;
  border: none;
  padding: 6px 14px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 0.85rem;
}
.close-icon {
  float: right;
  cursor: pointer;
  font-weight: bold;
  color: #999;
  margin-left: 10px;
  font-size: 16px;
  transition: color 0.2s ease;
}

.close-icon:hover {
  color: #333;
}
.close-icon {
  float: right;
  cursor: pointer;
  font-weight: bold;
  color: #cc0000;      /* Strong red color for visibility */
  margin-left: 12px;
  font-size: 22px;     /* Bigger size */
  line-height: 1;
  padding: 2px 6px;
  border-radius: 50%;
  background-color: #f8d7da;  /* Light red background circle */
  box-shadow: 0 2px 5px rgba(204, 0, 0, 0.4);
  transition: background-color 0.3s ease, color 0.3s ease;
  user-select: none;
}

.close-icon:hover {
  color: white;
  background-color: #cc0000;   /* Dark red on hover */
  box-shadow: 0 0 8px rgba(204, 0, 0, 0.7);
}

</style>
