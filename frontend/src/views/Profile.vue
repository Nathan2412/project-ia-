<template>
  <div class="profile">
    <h2 class="mb-4">Mon profil</h2>
    
    <!-- Profile information -->
    <div class="user-profile mb-4">
      <h3 class="mb-3">{{ $store.state.currentUser.name }}</h3>
      <hr>
      
      <div v-if="isEditing" class="edit-profile">
        <form @submit.prevent="saveChanges">
          <!-- Nom -->
          <div class="form-group mb-3">
            <label class="form-label">Nom d'utilisateur</label>
            <input type="text" class="form-control" v-model="userPrefs.name" required>
          </div>

          <!-- Genres aimés -->
          <div class="form-group mb-3">
            <label class="form-label">Genres que j'aime</label>
            <div v-if="$store.state.isLoading" class="text-center py-2">
              <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
            </div>
            <div v-else class="d-flex flex-wrap">
              <div v-for="genre in $store.state.genres" :key="genre"
                @click="toggleGenre(genre, 'likes')"
                class="tag" :class="{'tag-primary': userPrefs.genres_likes.includes(genre)}">
                {{ genre }}
              </div>
            </div>
          </div>
          
          <!-- Genres non aimés -->
          <div class="form-group mb-3">
            <label class="form-label">Genres que je n'aime pas</label>
            <div v-if="$store.state.isLoading" class="text-center py-2">
              <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
            </div>
            <div v-else class="d-flex flex-wrap">
              <div v-for="genre in $store.state.genres" :key="genre"
                @click="toggleGenre(genre, 'dislikes')"
                class="tag" :class="{'tag-secondary': userPrefs.genres_dislikes.includes(genre)}">
                {{ genre }}
              </div>
            </div>
          </div>
          
          <!-- Mots-clés -->
          <div class="form-group mb-3">
            <label class="form-label">Mots-clés d'intérêt</label>
            <input type="text" class="form-control" v-model="keywordsInput">
            <small class="form-text text-muted">Séparés par des virgules</small>
          </div>
          
          <!-- Réalisateurs -->
          <div class="form-group mb-3">
            <label class="form-label">Réalisateurs/créateurs préférés</label>
            <input type="text" class="form-control" v-model="directorsInput">
            <small class="form-text text-muted">Séparés par des virgules</small>
          </div>
          
          <!-- Note minimale -->
          <div class="form-group mb-3">
            <label class="form-label">Note minimale: {{ userPrefs.rating_min }}</label>
            <input type="range" class="form-range" min="1" max="10" step="0.5" v-model.number="userPrefs.rating_min">
          </div>
          
          <!-- Services de streaming -->
          <div class="form-group mb-3">
            <label class="form-label">Mes abonnements streaming</label>
            <div v-if="$store.state.isLoading" class="text-center py-2">
              <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
            </div>
            <div v-else class="d-flex flex-wrap">
              <div v-for="service in $store.state.streamingServices" :key="service"
                @click="toggleService(service)"
                class="tag" :class="{'tag-primary': userPrefs.streaming_services.includes(service)}">
                {{ service.charAt(0).toUpperCase() + service.slice(1) }}
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-end mt-4">
            <button type="button" @click="cancelEdit" class="btn btn-outline-secondary me-2">
              Annuler
            </button>
            <button type="submit" class="btn btn-primary" :disabled="$store.state.isLoading">
              <span v-if="$store.state.isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Enregistrer
            </button>
          </div>
        </form>
      </div>
      
      <!-- Display profile -->
      <div v-else class="user-preferences">
        <div class="row mb-3">
          <div class="col-md-4">
            <strong>Genres aimés:</strong>
          </div>
          <div class="col-md-8">
            <span v-for="genre in $store.state.currentUser.preferences.genres_likes" :key="genre" class="tag tag-primary me-1 mb-1">
              {{ genre }}
            </span>
            <span v-if="!$store.state.currentUser.preferences.genres_likes.length" class="text-muted">Aucun</span>
          </div>
        </div>
        
        <div class="row mb-3">
          <div class="col-md-4">
            <strong>Genres non aimés:</strong>
          </div>
          <div class="col-md-8">
            <span v-for="genre in $store.state.currentUser.preferences.genres_dislikes" :key="genre" class="tag tag-secondary me-1 mb-1">
              {{ genre }}
            </span>
            <span v-if="!$store.state.currentUser.preferences.genres_dislikes.length" class="text-muted">Aucun</span>
          </div>
        </div>
        
        <div class="row mb-3">
          <div class="col-md-4">
            <strong>Mots-clés d'intérêt:</strong>
          </div>
          <div class="col-md-8">
            {{ $store.state.currentUser.preferences.keywords_likes.join(', ') || 'Aucun' }}
          </div>
        </div>
        
        <div class="row mb-3">
          <div class="col-md-4">
            <strong>Réalisateurs/créateurs préférés:</strong>
          </div>
          <div class="col-md-8">
            {{ $store.state.currentUser.preferences.directors_likes.join(', ') || 'Aucun' }}
          </div>
        </div>
        
        <div class="row mb-3">
          <div class="col-md-4">
            <strong>Note minimale:</strong>
          </div>
          <div class="col-md-8">
            {{ $store.state.currentUser.preferences.rating_min }}
          </div>
        </div>
        
        <div class="row mb-3">
          <div class="col-md-4">
            <strong>Abonnements streaming:</strong>
          </div>
          <div class="col-md-8">
            <span v-for="service in $store.state.currentUser.preferences.streaming_services" :key="service" class="service-badge me-1">
              {{ service.charAt(0).toUpperCase() + service.slice(1) }}
            </span>
            <span v-if="!$store.state.currentUser.preferences.streaming_services.length" class="text-muted">Aucun</span>
          </div>
        </div>
        
        <div class="d-flex justify-content-end mt-4">
          <button @click="startEditing" class="btn btn-outline-primary">
            Modifier mes préférences
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'UserProfile',
  data() {
    return {
      isEditing: false,
      userPrefs: {
        name: '',
        genres_likes: [],
        genres_dislikes: [],
        directors_likes: [],
        keywords_likes: [],
        rating_min: 7.0,
        streaming_services: []
      },
      keywordsInput: '',
      directorsInput: ''
    };
  },
  created() {
    this.fetchGenres();
    this.fetchStreamingServices();
  },
  methods: {
    fetchGenres() {
      if (!this.$store.state.genres.length) {
        this.$store.dispatch('fetchGenres');
      }
    },
    fetchStreamingServices() {
      if (!this.$store.state.streamingServices.length) {
        this.$store.dispatch('fetchStreamingServices');
      }
    },
    startEditing() {
      // Clone current preferences
      this.userPrefs = {
        name: this.$store.state.currentUser.name || '',
        genres_likes: [...this.$store.state.currentUser.preferences.genres_likes || []],
        genres_dislikes: [...this.$store.state.currentUser.preferences.genres_dislikes || []],
        directors_likes: [...this.$store.state.currentUser.preferences.directors_likes || []],
        keywords_likes: [...this.$store.state.currentUser.preferences.keywords_likes || []],
        rating_min: this.$store.state.currentUser.preferences.rating_min || 7.0,
        streaming_services: [...this.$store.state.currentUser.preferences.streaming_services || []]
      };
      
      // Set input values
      this.keywordsInput = this.userPrefs.keywords_likes.join(', ');
      this.directorsInput = this.userPrefs.directors_likes.join(', ');
      
      this.isEditing = true;
    },
    cancelEdit() {
      this.isEditing = false;
    },
    toggleGenre(genre, type) {
      if (type === 'likes') {
        if (this.userPrefs.genres_likes.includes(genre)) {
          this.userPrefs.genres_likes = this.userPrefs.genres_likes.filter(g => g !== genre);
        } else {
          this.userPrefs.genres_likes.push(genre);
          // Remove from dislikes if necessary
          this.userPrefs.genres_dislikes = this.userPrefs.genres_dislikes.filter(g => g !== genre);
        }
      } else {
        if (this.userPrefs.genres_dislikes.includes(genre)) {
          this.userPrefs.genres_dislikes = this.userPrefs.genres_dislikes.filter(g => g !== genre);
        } else {
          this.userPrefs.genres_dislikes.push(genre);
          // Remove from likes if necessary
          this.userPrefs.genres_likes = this.userPrefs.genres_likes.filter(g => g !== genre);
        }
      }
    },
    toggleService(service) {
      if (this.userPrefs.streaming_services.includes(service)) {
        this.userPrefs.streaming_services = this.userPrefs.streaming_services.filter(s => s !== service);
      } else {
        this.userPrefs.streaming_services.push(service);
      }
    },
    async saveChanges() {
      // Parse inputs
      this.userPrefs.keywords_likes = this.keywordsInput.split(',')
        .map(k => k.trim())
        .filter(k => k !== '');
        
      this.userPrefs.directors_likes = this.directorsInput.split(',')
        .map(d => d.trim())
        .filter(d => d !== '');
      
      const success = await this.$store.dispatch('updateUserPreferences', this.userPrefs);
      if (success) {
        this.isEditing = false;
      }
    }
  }
}
</script>
