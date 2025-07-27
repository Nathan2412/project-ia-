<template>
  <div class="login-page">
    <AuthComponent />
  </div>
</template>

<script>
import AuthComponent from '@/components/AuthComponent.vue'

export default {
  name: 'LoginPage',
  components: {
    AuthComponent
  }
}
</script>

<style scoped>
.login-page {
  padding: 20px;
  min-height: 100vh;
  background-color: white;
}
</style>