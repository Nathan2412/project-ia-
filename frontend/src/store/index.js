import { createStore } from 'vuex';
import axios from 'axios';

// URL de base de l'API - configuration dynamique selon l'environnement
const API_URL = (() => {
  // En développement local
  if (process.env.NODE_ENV === 'development' || window.location.hostname === 'localhost') {
    return process.env.VUE_APP_API_URL || 'http://localhost:5000/api';
  }
  // En production
  return `${window.location.protocol}//${window.location.hostname}/api`;
})();

export default createStore({
  state: {
    currentUser: JSON.parse(localStorage.getItem('user')),
    users: [],
    recommendations: [],
    genres: [],
    streamingServices: [],
    isLoading: false,
    error: null
  },
  getters: {
    isLoggedIn: state => !!state.currentUser,
    currentUserId: state => state.currentUser ? state.currentUser.id : null
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
    setUsers(state, users) {
      state.users = users;
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
        state.currentUser.preferences = { ...state.currentUser.preferences, ...preferences };
        localStorage.setItem('user', JSON.stringify(state.currentUser));
      }
    }
  },
  actions: {
    // Récupérer la liste des utilisateurs
    async fetchUsers({ commit }) {
      commit('setLoading', true);
      commit('setError', null);
      
      try {
        const response = await axios.get(`${API_URL}/users`);
        commit('setUsers', response.data);
      } catch (error) {
        commit('setError', 'Erreur lors de la récupération des utilisateurs');
        console.error(error);
      } finally {
        commit('setLoading', false);
      }
    },
    
    // Récupérer les recommandations pour l'utilisateur actuel
    async fetchRecommendations({ commit, state }, { contentType = 'all', n = 5, streamingServices = [] }) {
      if (!state.currentUser) return;
      commit('setLoading', true);
      commit('setError', null);
      try {
        // Construction de l'URL avec gestion des services de streaming
        let url = `${API_URL}/recommendations/${state.currentUser.id}?content_type=${contentType}&n=${n}`;
        
        // Support du format moderne streamingServices (liste)
        if (streamingServices && streamingServices.length > 0) {
          // Utiliser le nouveau paramètre streaming_services au lieu de streaming_service
          url += `&streaming_services=${encodeURIComponent(streamingServices.join(','))}`;
        }
        
        console.log('🔍 Fetching recommendations from:', url);
        
        // Ajouter l'authentification si nécessaire
        const headers = {};
        const token = localStorage.getItem('auth_token');
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await axios.get(url, { headers });
        console.log('✅ Recommendations received:', response.data);
        
        commit('setRecommendations', response.data);
      } catch (error) {
        console.error('❌ Error fetching recommendations:', error);
        commit('setError', `Erreur lors de la récupération des recommandations: ${error.response?.data?.error || error.message}`);
      } finally {
        commit('setLoading', false);
      }
    },
    
    // Récupérer les genres disponibles
    async fetchGenres({ commit }) {
      commit('setLoading', true);
      commit('setError', null);
      
      try {
        const response = await axios.get(`${API_URL}/genres`);
        commit('setGenres', response.data);
      } catch (error) {
        commit('setError', 'Erreur lors de la récupération des genres');
        console.error(error);
      } finally {
        commit('setLoading', false);
      }
    },
    
    // Récupérer les services de streaming disponibles
    async fetchStreamingServices({ commit }) {
      commit('setLoading', true);
      commit('setError', null);
      
      try {
        const response = await axios.get(`${API_URL}/services`);
        commit('setStreamingServices', response.data);
      } catch (error) {
        commit('setError', 'Erreur lors de la récupération des services de streaming');
        console.error(error);
      } finally {
        commit('setLoading', false);
      }
    },
    
    // Se connecter avec un ID utilisateur
    // eslint-disable-next-line no-unused-vars
    async login({ commit, dispatch }, userId) {
      commit('setLoading', true);
      commit('setError', null);
      
      try {
        console.log('🔍 Attempting login for user ID:', userId);
        
        // Ajouter l'authentification si nécessaire
        const headers = {};
        const token = localStorage.getItem('auth_token');
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await axios.get(`${API_URL}/users/${userId}`, { headers });
        console.log('✅ Login successful:', response.data);
        
        commit('setCurrentUser', response.data);
        return true;
      } catch (error) {
        console.error('❌ Login error:', error);
        commit('setError', `Erreur lors de la connexion: ${error.response?.data?.error || error.message}`);
        return false;
      } finally {
        commit('setLoading', false);
      }
    },
    
    // Créer un nouvel utilisateur
    async createUser({ commit }, userData) {
      commit('setLoading', true);
      commit('setError', null);
      
      try {
        const response = await axios.post(`${API_URL}/users`, userData);
        commit('setCurrentUser', response.data);
        return true;
      } catch (error) {
        commit('setError', 'Erreur lors de la création de l\'utilisateur');
        console.error(error);
        return false;
      } finally {
        commit('setLoading', false);
      }
    },
    
    // Mettre à jour les préférences de l'utilisateur
    async updateUserPreferences({ commit, state }, preferences) {
      if (!state.currentUser) return false;
      
      commit('setLoading', true);
      commit('setError', null);
      
      try {
        await axios.put(`${API_URL}/users/${state.currentUser.id}`, preferences);
        commit('updateUserPreferences', preferences);
        return true;
      } catch (error) {
        commit('setError', 'Erreur lors de la mise à jour des préférences');
        console.error(error);
        return false;
      } finally {
        commit('setLoading', false);
      }
    },
      // Ajouter un élément à l'historique de l'utilisateur
    async addToHistory({ state, commit }, item) {
      if (!state.currentUser) return false;
      
      commit('setLoading', true);
      commit('setError', null);
      
      try {
        // Mise à jour de l'API pour correspondre au backend
        await axios.post(`${API_URL}/users/${state.currentUser.id}/history`, { 
          item: item 
        });
        
        // Mise à jour locale de l'historique
        if (!state.currentUser.watch_history) {
          commit('updateUserPreferences', { watch_history: [item] });
        } else {
          const updatedHistory = [...state.currentUser.watch_history, item];
          commit('updateUserPreferences', { watch_history: updatedHistory });
        }
        
        return true;
      } catch (error) {
        commit('setError', 'Erreur lors de l\'ajout à l\'historique');
        console.error(error);
        return false;
      } finally {
        commit('setLoading', false);
      }
    },
    
    // Se déconnecter
    logout({ commit }) {
      commit('setCurrentUser', null);
      commit('setRecommendations', []);
      localStorage.removeItem('auth_token');
    }
  }
});
