<template>
  <div class="login">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <ul class="nav nav-tabs card-header-tabs">
              <li class="nav-item">
                <a class="nav-link" :class="{ active: !showCreateAccount }" @click.prevent="showCreateAccount = false">
                  Connexion
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: showCreateAccount }" @click.prevent="showCreateAccount = true">
                  Créer un compte
                </a>
              </li>
            </ul>
          </div>
          
          <div class="card-body">
            <!-- Formulaire de connexion -->
            <div v-if="!showCreateAccount">
              <h5 class="card-title mb-4">Se connecter avec un profil existant</h5>
              
              <div v-if="$store.state.isLoading" class="loading-spinner">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Chargement...</span>
                </div>
              </div>
              
              <div v-else-if="$store.state.users.length === 0" class="text-center py-3">
                <p>Aucun utilisateur disponible.</p>
                <button @click="fetchUsers" class="btn btn-outline-primary">
                  Rafraîchir la liste
                </button>
              </div>
              
              <div v-else>
                <div class="list-group mb-4">
                  <button v-for="user in $store.state.users" :key="user.id"
                    @click="loginWithUser(user.id)"
                    class="list-group-item list-group-item-action">
                    {{ user.name }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- Formulaire de création de compte -->
            <div v-else>
              <h5 class="card-title mb-4">Créer un nouveau profil</h5>
              
              <form @submit.prevent="createNewUser">
                <div class="form-group mb-3">
                  <label for="name">Nom</label>
                  <input type="text" class="form-control" id="name" v-model="newUser.name" required>
                </div>
                
                <!-- Sélection des genres aimés -->
                <div class="form-group mb-3">
                  <label>Genres que vous aimez</label>
                  <div v-if="$store.state.isLoading" class="text-center py-2">
                    <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                  </div>
                  <div v-else class="d-flex flex-wrap">
                    <div v-for="genre in $store.state.genres" :key="genre" 
                      @click="toggleGenre(genre, 'likes')"
                      class="tag" :class="{'tag-primary': newUser.genres_likes.includes(genre)}">
                      {{ genre }}
                    </div>
                  </div>
                </div>
                
                <!-- Sélection des genres non aimés -->
                <div class="form-group mb-3">
                  <label>Genres que vous n'aimez pas</label>
                  <div v-if="$store.state.isLoading" class="text-center py-2">
                    <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                  </div>
                  <div v-else class="d-flex flex-wrap">
                    <div v-for="genre in $store.state.genres" :key="genre"
                      @click="toggleGenre(genre, 'dislikes')"
                      class="tag" :class="{'tag-secondary': newUser.genres_dislikes.includes(genre)}">
                      {{ genre }}
                    </div>
                  </div>
                </div>
                
                <!-- Mots-clés d'intérêt -->
                <div class="form-group mb-3">
                  <label for="keywords">Mots-clés d'intérêt (séparés par des virgules)</label>
                  <input type="text" class="form-control" id="keywords" v-model="keywordsInput">
                </div>
                
                <!-- Réalisateurs/créateurs préférés -->
                <div class="form-group mb-3">
                  <label for="directors">Réalisateurs/créateurs que vous appréciez (séparés par des virgules)</label>
                  <input type="text" class="form-control" id="directors" v-model="directorsInput">
                </div>
                
                <!-- Note minimale -->
                <div class="form-group mb-3">
                  <label for="rating">Note minimale (1-10)</label>
                  <input type="range" class="form-range" min="1" max="10" step="0.5" id="rating" v-model.number="newUser.rating_min">
                  <div class="text-center">{{ newUser.rating_min }}</div>
                </div>
                
                <!-- Services de streaming -->
                <div class="form-group mb-3">
                  <label>Services de streaming auxquels vous êtes abonné(e)</label>
                  <div v-if="$store.state.isLoading" class="text-center py-2">
                    <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                  </div>
                  <div v-else class="d-flex flex-wrap">
                    <div v-for="service in $store.state.streamingServices" :key="service"
                      @click="toggleService(service)"
                      class="tag" :class="{'tag-primary': newUser.streaming_services.includes(service)}">
                      {{ service.charAt(0).toUpperCase() + service.slice(1) }}
                    </div>
                  </div>
                </div>
                
                <div class="d-grid gap-2">
                  <button type="submit" class="btn btn-primary" :disabled="$store.state.isLoading">
                    <span v-if="$store.state.isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Créer mon profil
                  </button>
                </div>
              </form>
            </div>
            
            <div v-if="$store.state.error" class="alert alert-danger mt-3">
              {{ $store.state.error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  data() {
    return {
      showCreateAccount: false,
      newUser: {
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
    this.fetchUsers();
    this.fetchGenres();
    this.fetchStreamingServices();
  },
  methods: {
    fetchUsers() {
      this.$store.dispatch('fetchUsers');
    },
    fetchGenres() {
      this.$store.dispatch('fetchGenres');
    },
    fetchStreamingServices() {
      this.$store.dispatch('fetchStreamingServices');
    },
    async loginWithUser(userId) {
      const success = await this.$store.dispatch('login', userId);
      if (success) {
        // Rediriger vers la page de recommandations
        const redirect = this.$route.query.redirect || '/recommendations';
        this.$router.push(redirect);
      }
    },
    toggleGenre(genre, type) {
      if (type === 'likes') {
        if (this.newUser.genres_likes.includes(genre)) {
          this.newUser.genres_likes = this.newUser.genres_likes.filter(g => g !== genre);
        } else {
          this.newUser.genres_likes.push(genre);
          // Retirer des genres non aimés si nécessaire
          this.newUser.genres_dislikes = this.newUser.genres_dislikes.filter(g => g !== genre);
        }
      } else {
        if (this.newUser.genres_dislikes.includes(genre)) {
          this.newUser.genres_dislikes = this.newUser.genres_dislikes.filter(g => g !== genre);
        } else {
          this.newUser.genres_dislikes.push(genre);
          // Retirer des genres aimés si nécessaire
          this.newUser.genres_likes = this.newUser.genres_likes.filter(g => g !== genre);
        }
      }
    },
    toggleService(service) {
      if (this.newUser.streaming_services.includes(service)) {
        this.newUser.streaming_services = this.newUser.streaming_services.filter(s => s !== service);
      } else {
        this.newUser.streaming_services.push(service);
      }
    },
    async createNewUser() {
      // Préparation des données
      this.newUser.keywords_likes = this.keywordsInput.split(',')
        .map(keyword => keyword.trim())
        .filter(keyword => keyword !== '');
        
      this.newUser.directors_likes = this.directorsInput.split(',')
        .map(director => director.trim())
        .filter(director => director !== '');
      
      const success = await this.$store.dispatch('createUser', this.newUser);
      if (success) {
        this.$router.push('/recommendations');
      }
    }
  }
}
</script>
