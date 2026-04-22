<template>
  <div class="auth-container">
    <!-- Login form -->
    <div v-if="!showRegister" class="login-form">
      <h2>Connexion</h2>
      <form @submit.prevent="login">
        <div class="form-group">
          <label for="email">Email :</label>
          <input
            type="email"
            id="email"
            v-model="loginForm.email"
            required
            autocomplete="email"
            placeholder="votre@email.com"
          />
        </div>
        <div class="form-group">
          <label for="password">Mot de passe :</label>
          <input
            type="password"
            id="password"
            v-model="loginForm.password"
            required
            autocomplete="current-password"
            minlength="6"
          />
        </div>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Connexion...' : 'Se connecter' }}
        </button>
      </form>
      <p>
        Pas de compte ?
        <a href="#" @click.prevent="showRegister = true">S'inscrire</a>
      </p>
    </div>

    <!-- Registration form -->
    <div v-else class="register-form">
      <h2>Inscription</h2>
      <form @submit.prevent="register">
        <div class="form-group">
          <label for="reg-username">Nom d'utilisateur :</label>
          <input
            type="text"
            id="reg-username"
            v-model="registerForm.username"
            required
            minlength="3"
            autocomplete="username"
            placeholder="Votre nom"
          />
        </div>
        <div class="form-group">
          <label for="reg-email">Email :</label>
          <input
            type="email"
            id="reg-email"
            v-model="registerForm.email"
            required
            autocomplete="email"
            placeholder="votre@email.com"
          />
        </div>
        <div class="form-group">
          <label for="reg-password">Mot de passe :</label>
          <input
            type="password"
            id="reg-password"
            v-model="registerForm.password"
            required
            minlength="6"
            autocomplete="new-password"
            placeholder="Au moins 6 caractères"
          />
        </div>

        <div class="preferences">
          <h3>Préférences (optionnel)</h3>

          <div class="form-group">
            <label>Genres que vous aimez :</label>
            <div class="genre-buttons">
              <button
                v-for="genre in availableGenres"
                :key="genre"
                type="button"
                @click="toggleGenre(genre, 'likes')"
                :class="['genre-btn', { selected: registerForm.preferences.genres_likes.includes(genre) }]"
              >{{ genre }}</button>
            </div>
          </div>

          <div class="form-group">
            <label>Genres que vous n'aimez pas :</label>
            <div class="genre-buttons">
              <button
                v-for="genre in availableGenres"
                :key="genre"
                type="button"
                @click="toggleGenre(genre, 'dislikes')"
                :class="['genre-btn', 'dislike', { selected: registerForm.preferences.genres_dislikes.includes(genre) }]"
              >{{ genre }}</button>
            </div>
          </div>

          <div class="form-group">
            <label>Services de streaming :</label>
            <div class="streaming-buttons">
              <button
                v-for="service in streamingServices"
                :key="service"
                type="button"
                @click="toggleStreamingService(service)"
                :class="['streaming-btn', { selected: registerForm.preferences.streaming_services.includes(service) }]"
              >{{ capitalize(service) }}</button>
            </div>
          </div>

          <div class="form-group">
            <label>Note minimum :</label>
            <input
              type="number"
              v-model.number="registerForm.preferences.rating_min"
              min="1"
              max="10"
              step="0.1"
            />
          </div>
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Inscription...' : "S'inscrire" }}
        </button>
      </form>
      <p>
        Déjà un compte ?
        <a href="#" @click.prevent="showRegister = false">Se connecter</a>
      </p>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-if="success" class="success-message">{{ success }}</div>
  </div>
</template>

<script>
export default {
  name: 'AuthComponent',
  data() {
    return {
      showRegister: false,
      loading: false,
      error: '',
      success: '',
      loginForm: { email: '', password: '' },
      registerForm: {
        username: '',
        email: '',
        password: '',
        preferences: {
          genres_likes: [],
          genres_dislikes: [],
          rating_min: 7.0,
          streaming_services: []
        }
      },
      availableGenres: [
        'Action', 'Aventure', 'Animation', 'Comédie', 'Crime',
        'Documentaire', 'Drame', 'Famille', 'Fantaisie', 'Histoire',
        'Horreur', 'Musique', 'Mystère', 'Romance', 'Science-Fiction',
        'Thriller', 'Guerre', 'Western'
      ],
      streamingServices: ['netflix', 'amazon', 'disney', 'hbo', 'hulu', 'apple', 'peacock', 'paramount']
    };
  },
  async created() {
    await this.loadGenres();
  },
  methods: {
    capitalize(s) {
      return s ? s.charAt(0).toUpperCase() + s.slice(1) : '';
    },
    async login() {
      this.loading = true;
      this.error = '';
      this.success = '';
      const ok = await this.$store.dispatch('login', {
        email: this.loginForm.email,
        password: this.loginForm.password
      });
      this.loading = false;

      if (ok) {
        this.success = 'Connexion réussie !';
        this.loginForm = { email: '', password: '' };
        const redirect = this.$route?.query?.redirect || '/recommendations';
        this.$router.push(redirect);
      } else {
        this.error = this.$store.state.error || 'Erreur de connexion';
      }
    },
    async register() {
      this.loading = true;
      this.error = '';
      this.success = '';

      const payload = {
        name: this.registerForm.username,
        email: this.registerForm.email,
        password: this.registerForm.password,
        preferences: this.registerForm.preferences
      };
      const ok = await this.$store.dispatch('register', payload);
      this.loading = false;

      if (ok) {
        this.success = 'Inscription réussie !';
        this.registerForm = {
          username: '', email: '', password: '',
          preferences: { genres_likes: [], genres_dislikes: [], rating_min: 7.0, streaming_services: [] }
        };
        this.$router.push('/recommendations');
      } else {
        this.error = this.$store.state.error || "Erreur lors de l'inscription";
      }
    },
    async loadGenres() {
      try {
        await this.$store.dispatch('fetchGenres');
        if (this.$store.state.genres.length) {
          this.availableGenres = this.$store.state.genres;
        }
      } catch (e) {
        console.error('Erreur chargement genres:', e);
      }
    },
    toggleGenre(genre, type) {
      const field = type === 'likes' ? 'genres_likes' : 'genres_dislikes';
      const opposite = type === 'likes' ? 'genres_dislikes' : 'genres_likes';
      const list = this.registerForm.preferences[field];
      const idx = list.indexOf(genre);
      if (idx > -1) {
        list.splice(idx, 1);
      } else {
        list.push(genre);
        const oppIdx = this.registerForm.preferences[opposite].indexOf(genre);
        if (oppIdx > -1) this.registerForm.preferences[opposite].splice(oppIdx, 1);
      }
    },
    toggleStreamingService(service) {
      const list = this.registerForm.preferences.streaming_services;
      const idx = list.indexOf(service);
      if (idx > -1) list.splice(idx, 1);
      else list.push(service);
    }
  }
};
</script>

<style scoped>
.auth-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  color: #333;
}

.login-form, .register-form {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  background: white;
}

button {
  background: #007bff;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 10px;
}
button:hover { background: #0056b3; }
button:disabled { background: #6c757d; cursor: not-allowed; }

.error-message {
  background: #f8d7da;
  color: #721c24;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
  border: 1px solid #f5c6cb;
}
.success-message {
  background: #d4edda;
  color: #155724;
  padding: 15px;
  border-radius: 4px;
  margin: 20px 0;
  border: 1px solid #c3e6cb;
}
a { color: #007bff; text-decoration: none; }
a:hover { text-decoration: underline; }

.genre-buttons, .streaming-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}
.genre-btn, .streaming-btn {
  padding: 10px 16px;
  border: 2px solid #dee2e6;
  background: white;
  border-radius: 25px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  margin: 0;
  min-width: 80px;
}
.genre-btn:hover, .streaming-btn:hover {
  border-color: #007bff;
  background: #f8f9fa;
}
.genre-btn.selected {
  background: #007bff;
  color: white;
  border-color: #007bff;
}
.genre-btn.dislike.selected {
  background: #dc3545;
  color: white;
  border-color: #dc3545;
}
.streaming-btn.selected {
  background: #28a745;
  color: white;
  border-color: #28a745;
}
.preferences {
  border: 1px solid #dee2e6;
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  background: #f8f9fa;
}
</style>
