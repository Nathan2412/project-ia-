<template>
  <div class="recommendations">
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
                  {{ service.charAt(0).toUpperCase() + service.slice(1) }}
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
            <button @click="getRecommendations" class="btn btn-primary w-100">
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
    <div v-else-if="$store.state.recommendations.length === 0" class="text-center py-5">
      <div class="alert alert-info">
        <p>Aucune recommandation trouvée avec les critères actuels.</p>
        <p>Essayez de modifier vos filtres ou vos préférences.</p>
      </div>
    </div>    <!-- Recommendations display -->
    <div v-else class="row">
      <div v-for="(rec, index) in $store.state.recommendations" :key="index" class="col-md-4 mb-4">
        <MovieCard 
          :item="rec.item" 
          :type="rec.type" 
          :streaming-services="rec.streaming_services"
          :in-history="checkIfInHistory(rec.item.id, rec.type)"
          @add-to-history="addToHistory(rec.item, rec.type)"
          @show-details="showItemDetails(rec.item, rec.type)"
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
    async loadDependencies() {
      await this.$store.dispatch('fetchStreamingServices');
    },
    getRecommendations() {
      this.$store.dispatch('fetchRecommendations', {
        contentType: this.filters.contentType,
        n: this.filters.n,
        streamingServices: this.filters.streamingServices
      });
    },    truncateText(text, length) {
      if (!text) return '';
      if (text.length <= length) return text;
      return text.substring(0, length) + '...';
    },
    checkIfInHistory(itemId, type) {
      if (!this.$store.state.currentUser || !this.$store.state.currentUser.watch_history) {
        return false;
      }
      return this.$store.state.currentUser.watch_history.some(item => 
        item.id === itemId && item.content_type === type
      );
    },
    async addToHistory(item, type) {
      try {
        await this.$store.dispatch('addToHistory', {
          id: item.id,
          title: item.title || item.name,
          poster_path: item.poster_path,
          content_type: type,
          rating: item.rating
        });
        
        // Notification de succès
        this.$root.$refs.notifications.success(
          `"${item.title || item.name}" a été ajouté à votre historique!`
        );
        
        // Rafraîchir les recommandations
        setTimeout(() => this.getRecommendations(), 1000);
      } catch (error) {
        this.$root.$refs.notifications.error(
          "Erreur lors de l'ajout à l'historique."
        );
        console.error(error);
      }
    },
    // eslint-disable-next-line no-unused-vars
    showItemDetails(item, type) {
      // Afficher un dialogue modal avec plus de détails sur le film/série
      // Pour une version ultérieure, on pourrait créer un modal ou une page détaillée
      console.log('Afficher détails pour:', item);
      this.$root.$refs.notifications.info(
        `Détails de "${item.title || item.name}" - Cette fonctionnalité sera disponible dans une prochaine version.`
      );
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
