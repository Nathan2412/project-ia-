<template>
  <div class="notification-wrapper">
    <transition-group name="notification">
      <div v-for="notification in notifications" 
          :key="notification.id" 
          class="notification" 
          :class="[notification.type]">
        <div class="notification-content">
          {{ notification.message }}
        </div>
        <button class="notification-close" @click="removeNotification(notification.id)">
          &times;
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script>
export default {
  name: 'NotificationSystem',
  data() {
    return {
      notifications: [],
      nextId: 1
    };
  },
  methods: {
    addNotification(message, type = 'info', timeout = 5000) {
      const id = this.nextId++;
      const notification = { id, message, type };
      this.notifications.push(notification);
      
      // Auto-remove after timeout
      if (timeout !== 0) {
        setTimeout(() => {
          this.removeNotification(id);
        }, timeout);
      }
      
      return id;
    },
    removeNotification(id) {
      const index = this.notifications.findIndex(n => n.id === id);
      if (index !== -1) {
        this.notifications.splice(index, 1);
      }
    },
    success(message, timeout = 5000) {
      return this.addNotification(message, 'success', timeout);
    },
    error(message, timeout = 5000) {
      return this.addNotification(message, 'error', timeout);
    },
    info(message, timeout = 5000) {
      return this.addNotification(message, 'info', timeout);
    },
    warning(message, timeout = 5000) {
      return this.addNotification(message, 'warning', timeout);
    }
  }
};
</script>

<style scoped>
.notification-wrapper {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  width: 300px;
}

.notification {
  padding: 12px 15px;
  margin-bottom: 10px;
  border-radius: 4px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
  background-color: #333;
}

.notification.success {
  background-color: #28a745;
}

.notification.error {
  background-color: #dc3545;
}

.notification.info {
  background-color: #17a2b8;
}

.notification.warning {
  background-color: #ffc107;
  color: #333;
}

.notification-content {
  flex-grow: 1;
  padding-right: 10px;
}

.notification-close {
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  font-size: 18px;
  padding: 0;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.notification-close:hover {
  opacity: 1;
}

/* Transition animations */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(50px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateY(-30px);
}
</style>
