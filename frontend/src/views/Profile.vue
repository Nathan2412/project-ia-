<template>
  <div class="profile container">
    <h2 class="mb-4">Mon profil</h2>

    <div class="user-profile mb-4">
      <h3 class="mb-3">{{ currentUser.name }}</h3>
      <hr>

      <!-- Edit mode -->
      <div v-if="isEditing" class="edit-profile">
        <form @submit.prevent="saveChanges">
          <div class="form-group mb-3">
            <label class="form-label">Nom d'utilisateur</label>
            <input type="text" class="form-control" v-model="userPrefs.name" required>
          </div>

          <div class="form-group mb-3">
            <label class="form-label">Genres que j'aime</label>
            <div v-if="$store.state.isLoading && !$store.state.genres.length" class="text-center py-2">
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

          <div class="form-group mb-3">
            <label class="form-label">Genres que je n'aime pas</label>
            <div class="d-flex flex-wrap">
              <div v-for="genre in $store.state.genres" :key="genre"
                @click="toggleGenre(genre, 'dislikes')"
                class="tag" :class="{'tag-secondary': userPrefs.genres_dislikes.includes(genre)}">
                {{ genre }}
              </div>
            </div>
          </div>

          <div class="form-group mb-3">
            <label class="form-label">Mots-clés d'intérêt</label>
            <input type="text" class="form-control" v-model="keywordsInput">
            <small class="form-text text-muted">Séparés par des virgules</small>
          </div>

          <div class="form-group mb-3">
            <label class="form-label">Réalisateurs/créateurs préférés</label>
            <input type="text" class="form-control" v-model="directorsInput">
            <small class="form-text text-muted">Séparés par des virgules</small>
          </div>

          <div class="form-group mb-3">
            <label class="form-label">Note minimale : {{ userPrefs.rating_min }}</label>
            <input type="range" class="form-range" min="1" max="10" step="0.5" v-model.number="userPrefs.rating_min">
          </div>

          <div class="form-group mb-3">
            <label class="form-label">Mes abonnements streaming</label>
            <div class="d-flex flex-wrap">
              <div v-for="service in $store.state.streamingServices" :key="service"
                @click="toggleService(service)"
                class="tag" :class="{'tag-primary': userPrefs.streaming_services.includes(service)}">
                {{ capitalize(service) }}
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

      <!-- Display mode -->
      <div v-else class="user-preferences">
        <div class="row mb-3">
          <div class="col-md-4"><strong>Genres aimés :</strong></div>
          <div class="col-md-8">
            <span v-for="genre in preferences.genres_likes" :key="genre" class="tag tag-primary me-1 mb-1">
              {{ genre }}
            </span>
            <span v-if="!preferences.genres_likes.length" class="text-muted">Aucun</span>
          </div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4"><strong>Genres non aimés :</strong></div>
          <div class="col-md-8">
            <span v-for="genre in preferences.genres_dislikes" :key="genre" class="tag tag-secondary me-1 mb-1">
              {{ genre }}
            </span>
            <span v-if="!preferences.genres_dislikes.length" class="text-muted">Aucun</span>
          </div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4"><strong>Mots-clés d'intérêt :</strong></div>
          <div class="col-md-8">
            {{ preferences.keywords_likes.join(', ') || 'Aucun' }}
          </div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4"><strong>Réalisateurs/créateurs :</strong></div>
          <div class="col-md-8">
            {{ preferences.directors_likes.join(', ') || 'Aucun' }}
          </div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4"><strong>Note minimale :</strong></div>
          <div class="col-md-8">{{ preferences.rating_min }}</div>
        </div>

        <div class="row mb-3">
          <div class="col-md-4"><strong>Abonnements streaming :</strong></div>
          <div class="col-md-8">
            <span v-for="service in preferences.streaming_services" :key="service" class="service-badge me-1">
              {{ capitalize(service) }}
            </span>
            <span v-if="!preferences.streaming_services.length" class="text-muted">Aucun</span>
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
const EMPTY_PREFS = {
  genres_likes: [],
  genres_dislikes: [],
  directors_likes: [],
  keywords_likes: [],
  rating_min: 7.0,
  streaming_services: []
};

export default {
  name: 'UserProfile',
  inject: {
    notify: { default: null }
  },
  data() {
    return {
      isEditing: false,
      userPrefs: {
        name: '',
        ...EMPTY_PREFS
      },
      keywordsInput: '',
      directorsInput: ''
    };
  },
  computed: {
    currentUser() {
      return this.$store.state.currentUser || { name: '', preferences: {} };
    },
    preferences() {
      const p = this.currentUser.preferences || {};
      return {
        genres_likes: p.genres_likes || [],
        genres_dislikes: p.genres_dislikes || [],
        directors_likes: p.directors_likes || [],
        keywords_likes: p.keywords_likes || [],
        rating_min: p.rating_min ?? 7.0,
        streaming_services: p.streaming_services || []
      };
    }
  },
  created() {
    if (!this.$store.state.genres.length) {
      this.$store.dispatch('fetchGenres');
    }
    if (!this.$store.state.streamingServices.length) {
      this.$store.dispatch('fetchStreamingServices');
    }
  },
  methods: {
    capitalize(s) {
      return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
    },
    startEditing() {
      this.userPrefs = {
        name: this.currentUser.name || '',
        genres_likes: [...this.preferences.genres_likes],
        genres_dislikes: [...this.preferences.genres_dislikes],
        directors_likes: [...this.preferences.directors_likes],
        keywords_likes: [...this.preferences.keywords_likes],
        rating_min: this.preferences.rating_min,
        streaming_services: [...this.preferences.streaming_services]
      };
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
          this.userPrefs.genres_dislikes = this.userPrefs.genres_dislikes.filter(g => g !== genre);
        }
      } else {
        if (this.userPrefs.genres_dislikes.includes(genre)) {
          this.userPrefs.genres_dislikes = this.userPrefs.genres_dislikes.filter(g => g !== genre);
        } else {
          this.userPrefs.genres_dislikes.push(genre);
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
      this.userPrefs.keywords_likes = this.keywordsInput.split(',')
        .map(k => k.trim()).filter(Boolean);
      this.userPrefs.directors_likes = this.directorsInput.split(',')
        .map(d => d.trim()).filter(Boolean);

      const success = await this.$store.dispatch('updateUserPreferences', this.userPrefs);
      if (success) {
        this.isEditing = false;
        if (this.notify) this.notify('Préférences mises à jour !', 'success');
      } else if (this.notify) {
        this.notify('Erreur lors de la sauvegarde des préférences.', 'error');
      }
    }
  }
}
</script>

<style scoped>
.tag {
  display: inline-block;
  padding: 6px 12px;
  margin: 4px;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  cursor: pointer;
  user-select: none;
  background: #fff;
  transition: all 0.2s;
}
.tag:hover { border-color: #0d6efd; }
.tag.tag-primary {
  background: #0d6efd;
  color: white;
  border-color: #0d6efd;
}
.tag.tag-secondary {
  background: #6c757d;
  color: white;
  border-color: #6c757d;
}
.service-badge {
  display: inline-block;
  padding: 4px 10px;
  background: #e9ecef;
  border-radius: 12px;
  font-size: 0.85rem;
}
</style>
