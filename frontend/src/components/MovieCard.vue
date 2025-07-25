<template>
  <div class="card movie-card h-100">
    <!-- Poster image -->
    <div v-if="item.poster_path" class="poster-container">
      <img :src="`https://image.tmdb.org/t/p/w500${item.poster_path}`" :alt="item.title" class="movie-poster card-img-top">
    </div>
    <div v-else class="movie-poster-placeholder card-img-top d-flex justify-content-center align-items-center bg-light">
      <span class="text-muted">Pas d'image disponible</span>
    </div>
    
    <div class="card-body d-flex flex-column">
      <h5 class="movie-title">{{ item.title }}</h5>
      
      <div class="movie-info">
        <span>{{ item.year }}</span>
        <span>
          {{ type === 'movie' ? 'Film' : 'Série' }} • 
          <span class="star-rating">
            <i class="fas fa-star"></i> {{ item.rating.toFixed(1) }}
          </span>
        </span>
      </div>
      
      <p class="movie-genres mb-2">
        <small>
          <span v-for="(genre, idx) in item.genre" :key="genre">
            {{ genre }}{{ idx < item.genre.length - 1 ? ', ' : '' }}
          </span>
        </small>
      </p>
      
      <div v-if="streamingServices && streamingServices.length > 0" class="mb-2">
        <span v-for="service in streamingServices" :key="service" class="service-badge">
          {{ service.charAt(0).toUpperCase() + service.slice(1) }}
        </span>
      </div>
      
      <p class="movie-overview flex-grow-1">{{ truncateOverview(item.overview) }}</p>
      
      <div class="mt-auto d-flex justify-content-between">
        <button v-if="!inHistory" @click="addToHistory" class="btn btn-sm btn-outline-primary">
          Ajouter à mon historique
        </button>
        <span v-else class="text-success">
          <i class="fas fa-check"></i> Dans votre historique
        </span>
        
        <a href="#" @click.prevent="showDetails" class="btn btn-sm btn-link">
          Plus de détails
        </a>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MovieCard',
  props: {
    item: {
      type: Object,
      required: true
    },
    type: {
      type: String,
      default: 'movie'
    },
    streamingServices: {
      type: Array,
      default: () => []
    },
    inHistory: {
      type: Boolean,
      default: false
    }
  },
  methods: {
    truncateOverview(text) {
      if (!text) return '';
      return text.length > 100 ? text.substring(0, 100) + '...' : text;
    },
    addToHistory() {
      this.$emit('add-to-history', {
        id: this.item.id,
        title: this.item.title,
        poster_path: this.item.poster_path,
        content_type: this.type,
        rating: this.item.rating
      });
    },
    showDetails() {
      this.$emit('show-details', this.item);
    }
  }
}
</script>

<style scoped>
.movie-poster {
  height: 300px;
  object-fit: cover;
}

.movie-poster-placeholder {
  height: 300px;
  background-color: #f8f9fa;
}

.movie-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.movie-genres {
  font-size: 0.85rem;
  color: #6c757d;
}

.movie-overview {
  font-size: 0.9rem;
  line-height: 1.4;
}

.service-badge {
  display: inline-block;
  background-color: #e9ecef;
  color: #495057;
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 16px;
  margin-right: 5px;
  margin-bottom: 5px;
}

.star-rating {
  color: #ffc107;
}
</style>
