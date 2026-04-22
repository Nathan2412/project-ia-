import { createStore } from 'vuex';
import axios from 'axios';

// URL de base de l'API - mode LOCAL uniquement
const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:5000/api';

// Intercepteur global : ajoute automatiquement le token JWT à toutes les requêtes
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Helper pour parser le user en local storage en toute sécurité
function safeParseUser() {
  try {
    const raw = localStorage.getItem('user');
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    console.error('Erreur parsing user en localStorage', e);
    localStorage.removeItem('user');
    return null;
  }
}

export default createStore({
  state: {
    currentUser: safeParseUser(),
    users: [],
    recommendations: [],
    genres: [],
    streamingServices: [],
    isLoading: false,
    error: null
  },
  getters: {
    isLoggedIn: state => !!state.currentUser && !!localStorage.getItem('auth_token'),
    currentUserId: state => (state.currentUser ? state.currentUser.id : null)
  },
  mutations: {
    setCurrentUser(state, user) {
      state.currentUser = user;
      if (user) {
        localStorage.setItem('user', JSON.stringify(user));
      } else {
        localStorage.removeItem('user');
      }
    },
    setToken(_state, token) {
      if (token) {
        localStorage.setItem('auth_token', token);
      } else {
        localStorage.removeItem('auth_token');
      }
    },
    setRecommendations(state, recommendations) {
      state.recommendations = recommendations;
    },
    setGenres(state, genres) {
      state.genres = genres;
    },
    setStreamingServices(state, services) {
      state.streamingServices = services;
    },
    setLoading(state, isLoading) {
      state.isLoading = isLoading;
    },
    setError(state, error) {
      state.error = error;
    },
    updateUserPreferences(state, preferences) {
      if (state.currentUser) {
        state.currentUser.preferences = {
          ...(state.currentUser.preferences || {}),
          ...preferences
        };
        localStorage.setItem('user', JSON.stringify(state.currentUser));
      }
    }
  },
  actions: {
    // Connexion avec email/password
    async login({ commit }, { email, password }) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.post(`${API_URL}/login`, { email, password });
        commit('setToken', response.data.token);
        commit('setCurrentUser', response.data.user);
        return true;
      } catch (error) {
        const msg = error.response?.data?.error || error.message;
        commit('setError', `Erreur lors de la connexion: ${msg}`);
        return false;
      } finally {
        commit('setLoading', false);
      }
    },

    // Inscription
    async register({ commit }, userData) {
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.post(`${API_URL}/register`, userData);
        commit('setToken', response.data.token);
        commit('setCurrentUser', response.data.user);
        return true;
      } catch (error) {
        const msg = error.response?.data?.error || error.message;
        commit('setError', `Erreur lors de l'inscription: ${msg}`);
        return false;
      } finally {
        commit('setLoading', false);
      }
    },

    // Vérifier la validité du token au démarrage
    async verifyToken({ commit }) {
      const token = localStorage.getItem('auth_token');
      if (!token) return false;
      try {
        const response = await axios.get(`${API_URL}/verify-token`);
        commit('setCurrentUser', response.data.user);
        return true;
      } catch (error) {
        // Token invalide ou expiré
        commit('setToken', null);
        commit('setCurrentUser', null);
        return false;
      }
    },

    // Récupérer les recommandations pour l'utilisateur actuel
    async fetchRecommendations({ commit, state }, { contentType = 'all', n = 5, streamingServices = [] } = {}) {
      if (!state.currentUser) return;
      commit('setLoading', true);
      commit('setError', null);
      try {
        const params = { content_type: contentType, n };
        if (streamingServices && streamingServices.length > 0) {
          params.streaming_services = streamingServices.join(',');
        }
        const response = await axios.get(
          `${API_URL}/recommendations/${state.currentUser.id}`,
          { params }
        );
        commit('setRecommendations', response.data);
      } catch (error) {
        const msg = error.response?.data?.error || error.message;
        commit('setError', `Erreur lors de la récupération des recommandations: ${msg}`);
      } finally {
        commit('setLoading', false);
      }
    },

    // Récupérer les genres disponibles
    async fetchGenres({ commit }) {
      commit('setError', null);
      try {
        const response = await axios.get(`${API_URL}/genres`);
        commit('setGenres', response.data);
      } catch (error) {
        commit('setError', 'Erreur lors de la récupération des genres');
      }
    },

    // Récupérer les services de streaming
    async fetchStreamingServices({ commit }) {
      commit('setError', null);
      try {
        const response = await axios.get(`${API_URL}/services`);
        commit('setStreamingServices', response.data);
      } catch (error) {
        commit('setError', 'Erreur lors de la récupération des services');
      }
    },

    // Mettre à jour les préférences de l'utilisateur
    async updateUserPreferences({ commit, state }, preferences) {
      if (!state.currentUser) return false;
      commit('setLoading', true);
      commit('setError', null);
      try {
        const response = await axios.put(
          `${API_URL}/users/${state.currentUser.id}`,
          preferences
        );
        // Le backend renvoie l'utilisateur mis à jour
        commit('setCurrentUser', response.data);
        return true;
      } catch (error) {
        const msg = error.response?.data?.error || error.message;
        commit('setError', `Erreur lors de la mise à jour des préférences: ${msg}`);
        return false;
      } finally {
        commit('setLoading', false);
      }
    },

    // Ajouter un élément à l'historique
    async addToHistory({ state, commit }, item) {
      if (!state.currentUser) return false;
      commit('setError', null);
      try {
        await axios.post(
          `${API_URL}/users/${state.currentUser.id}/history`,
          { item }
        );
        const currentHistory = state.currentUser.preferences?.watch_history || [];
        commit('updateUserPreferences', { watch_history: [...currentHistory, item] });
        return true;
      } catch (error) {
        const msg = error.response?.data?.error || error.message;
        commit('setError', `Erreur lors de l'ajout à l'historique: ${msg}`);
        return false;
      }
    },

    // Déconnexion
    logout({ commit }) {
      commit('setCurrentUser', null);
      commit('setToken', null);
      commit('setRecommendations', []);
    }
  }
});
