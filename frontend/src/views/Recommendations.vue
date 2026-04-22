<template>
  <div class="recommendations container">
    <h2 class="mb-4">Recommandations pour vous</h2>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="card-title">Filtres</h5>
        <div class="row align-items-end">
          <div class="col-md-4">
            <div class="form-group">
              <label>Type de contenu</label>
              <select v-model="filters.contentType" class="form-select">
                <option value="all">Films et Séries</option>
                <option value="movies">Films uniquement</option>
                <option value="series">Séries uniquement</option>
              </select>
            </div>
          </div>
          <div class="col-md-4">
            <div class="form-group">
              <label>Services de streaming</label>
              <select v-model="filters.streamingServices" class="form-select" multiple>
                <option v-for="service in $store.state.streamingServices" :key="service" :value="service">
                  {{ capitalize(service) }}
                </option>
              </select>
            </div>
          </div>
          <div class="col-md-2">
            <div class="form-group">
              <label>Nombre de résultats</label>
              <input type="number" v-model.number="filters.n" min="1" max="20" class="form-control">
            </div>
          </div>
          <div class="col-md-2">
            <button @click="getRecommendations" class="btn btn-primary w-100" :disabled="$store.state.isLoading">
              Appliquer
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="$store.state.isLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Chargement...</span>
      </div>
      <p class="mt-3">Recherche de recommandations en cours...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="$store.state.error" class="alert alert-danger">
      {{ $store.state.error }}
      <button @click="getRecommendations" class="btn btn-outline-danger btn-sm ms-2">Réessayer</button>
    </div>

    <!-- No recommendations -->
    <div v-else-if="!$store.state.recommendations.length" class="text-center py-5">
      <div class="alert alert-info">
        <p>Aucune recommandation trouvée avec les critères actuels.</p>
        <p>Essayez de modifier vos filtres ou vos préférences.</p>
      </div>
    </div>

    <!-- Recommendations display -->
    <div v-else class="row">
      <div v-for="(rec, index) in $store.state.recommendations" :key="recKey(rec, index)" class="col-md-4 mb-4">
        <MovieCard
          :item="recItem(rec)"
          :type="rec.type || 'movie'"
          :streaming-services="rec.streaming_services || []"
          :in-history="checkIfInHistory(recItem(rec).id, rec.type)"
          @add-to-history="onAddToHistory(recItem(rec), rec.type)"
          @show-details="onShowDetails(recItem(rec))"
        />
      </div>
    </div>
  </div>
</template>

<script>
import MovieCard from '@/components/MovieCard.vue';

export default {
  name: 'MovieRecommendations',
  components: {
    MovieCard
  },
  inject: {
    notify: { default: null }
  },
  data() {
    return {
      filters: {
        contentType: 'all',
        streamingServices: [],
        n: 10
      }
    };
  },
  created() {
    this.loadDependencies();
    this.getRecommendations();
  },
  methods: {
    capitalize(s) {
      return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
    },
    async loadDependencies() {
      await this.$store.dispatch('fetchStreamingServices');
    },
    getRecommendations() {
      this.$store.dispatch('fetchRecommendations', {
        contentType: this.filters.contentType,
        n: this.filters.n,
        streamingServices: this.filters.streamingServices
      });
    },
    // Le backend retourne une liste d'objets plats (formattés via RecommendationFormatter)
    // mais aussi parfois des objets { item, type, ... } - supporter les deux
    recItem(rec) {
      return rec?.item || rec || {};
    },
    recKey(rec, index) {
      const item = this.recItem(rec);
      return item.id ? `${item.id}-${rec.type || 'x'}` : `rec-${index}`;
    },
    checkIfInHistory(itemId, type) {
      const user = this.$store.state.currentUser;
      const history = user?.preferences?.watch_history || user?.watch_history || [];
      return history.some(item => item.id === itemId && item.content_type === type);
    },
    async onAddToHistory(item, type) {
      const payload = {
        id: item.id,
        title: item.title || item.name,
        poster_path: item.poster_path,
        content_type: type,
        rating: item.rating
      };
      const success = await this.$store.dispatch('addToHistory', payload);
      if (success && this.notify) {
        this.notify(`"${payload.title}" a été ajouté à votre historique !`, 'success');
      } else if (!success && this.notify) {
        this.notify("Erreur lors de l'ajout à l'historique.", 'error');
      }
    },
    onShowDetails(item) {
      if (this.notify) {
        this.notify(
          `Détails de "${item.title || item.name}" - Fonctionnalité à venir.`,
          'info'
        );
      }
    }
  }
}
</script>

<style scoped>
.poster-container {
  height: 350px;
  overflow: hidden;
}

.movie-poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movie-poster-placeholder {
  height: 350px;
}

.compatibility-score {
  font-size: 0.9rem;
  color: #6200ea;
}
</style>
