<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-light bg-white">
      <div class="container">
        <router-link class="navbar-brand" to="/">WhatToWatch</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Accueil</router-link>
            </li>
            <li class="nav-item" v-if="isLoggedIn">
              <router-link class="nav-link" to="/recommendations">Recommandations</router-link>
            </li>
            <li class="nav-item" v-if="isLoggedIn">
              <router-link class="nav-link" to="/profile">Mon profil</router-link>
            </li>
          </ul>
          <div class="d-flex">
            <div v-if="isLoggedIn" class="d-flex align-items-center">
              <span class="me-3">Bienvenue, {{ currentUser.name }}</span>
              <button @click="logout" class="btn btn-outline-danger">Déconnexion</button>
            </div>
            <router-link v-else to="/login" class="btn btn-primary">Connexion</router-link>
          </div>
        </div>
      </div>
    </nav>

    <div class="app-container">
      <router-view/>
    </div>

    <NotificationSystem ref="notifications" />

    <footer class="bg-light py-4 mt-5">
      <div class="container text-center">
        <p>© 2025 FilmRecommender - Système de recommandation de films et séries</p>
      </div>
    </footer>
  </div>
</template>

<script>
import NotificationSystem from './components/NotificationSystem.vue';

export default {
  name: 'App',
  components: {
    NotificationSystem
  },
  computed: {
    isLoggedIn() {
      return this.$store.getters.isLoggedIn;
    },
    currentUser() {
      return this.$store.state.currentUser || { name: '' };
    }
  },
  async created() {
    // Au démarrage, vérifier la validité du token côté backend
    // pour éviter d'afficher un faux état connecté
    if (localStorage.getItem('auth_token')) {
      await this.$store.dispatch('verifyToken');
    }
  },
  methods: {
    async logout() {
      await this.$store.dispatch('logout');
      this.$router.push('/login');
      if (this.$refs.notifications) {
        this.$refs.notifications.success('Vous avez été déconnecté avec succès.');
      }
    },
    notify(message, type = 'info', timeout = 5000) {
      if (this.$refs.notifications) {
        return this.$refs.notifications.addNotification(message, type, timeout);
      }
    }
  },
  provide() {
    return {
      notify: this.notify
    };
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-container {
  flex: 1;
  width: 100%;
  padding: 20px 0;
  box-sizing: border-box;
}

.navbar {
  width: 100%;
  z-index: 1000;
}

footer {
  margin-top: auto;
  width: 100%;
}
</style>
