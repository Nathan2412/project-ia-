<!-- Composant Vue.js pour la gestion de l'authentification -->
<template>
  <div class="auth-container">
    <!-- Page de connexion/inscription -->
    <div v-if="!isAuthenticated" class="auth-forms">
      <!-- Formulaire de connexion -->
      <div v-if="!showRegister" class="login-form">
        <h2>Connexion</h2>
        <form @submit.prevent="login">
          <div class="form-group">
            <label for="username">Nom d'utilisateur:</label>
            <input
              type="text"
              id="username"
              v-model="loginForm.username"
              required
            />
          </div>
          <div class="form-group">
            <label for="password">Mot de passe:</label>
            <input
              type="password"
              id="password"
              v-model="loginForm.password"
              required
            />
          </div>
          <button type="submit" :disabled="loading">
            {{ loading ? 'Connexion...' : 'Se connecter' }}
          </button>
        </form>
        <p>
          Pas de compte ? 
          <a href="#" @click="showRegister = true">S'inscrire</a>
        </p>
        
        <!-- Informations pour les utilisateurs existants -->
        <div class="existing-users-info">
          <h3>Utilisateurs existants :</h3>
          <p><strong>Alice</strong> - mot de passe : password123</p>
          <p><strong>Bob</strong> - mot de passe : password123</p>
          <p><strong>nathan</strong> - mot de passe : password123</p>
          <p><em>Changez votre mot de passe après la première connexion !</em></p>
        </div>
      </div>

      <!-- Formulaire d'inscription -->
      <div v-else class="register-form">
        <h2>Inscription</h2>
        <form @submit.prevent="register">
          <div class="form-group">
            <label for="reg-username">Nom d'utilisateur:</label>
            <input
              type="text"
              id="reg-username"
              v-model="registerForm.username"
              required
              minlength="3"
            />
          </div>
          <div class="form-group">
            <label for="reg-password">Mot de passe:</label>
            <input
              type="password"
              id="reg-password"
              v-model="registerForm.password"
              required
              minlength="6"
            />
          </div>
          
          <!-- Préférences -->
          <div class="preferences">
            <h3>Préférences (optionnel)</h3>
            <div class="form-group">
              <label>Genres préférés:</label>
              <select multiple v-model="registerForm.preferences.genres_likes">
                <option v-for="genre in availableGenres" :key="genre" :value="genre">
                  {{ genre }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label>Note minimum:</label>
              <input
                type="number"
                v-model="registerForm.preferences.rating_min"
                min="1"
                max="10"
                step="0.1"
              />
            </div>
          </div>
          
          <button type="submit" :disabled="loading">
            {{ loading ? 'Inscription...' : 'S\'inscrire' }}
          </button>
        </form>
        <p>
          Déjà un compte ? 
          <a href="#" @click="showRegister = false">Se connecter</a>
        </p>
      </div>
    </div>

    <!-- Interface utilisateur connecté -->
    <div v-else class="user-dashboard">
      <div class="user-header">
        <h2>Bienvenue, {{ currentUser.name }} !</h2>
        <div class="user-actions">
          <button @click="showChangePassword = true">Changer le mot de passe</button>
          <button @click="logout">Déconnexion</button>
        </div>
      </div>

      <!-- Changement de mot de passe -->
      <div v-if="showChangePassword" class="change-password">
        <h3>Changer le mot de passe</h3>
        <form @submit.prevent="changePassword">
          <div class="form-group">
            <label>Mot de passe actuel:</label>
            <input
              type="password"
              v-model="changePasswordForm.current_password"
              required
            />
          </div>
          <div class="form-group">
            <label>Nouveau mot de passe:</label>
            <input
              type="password"
              v-model="changePasswordForm.new_password"
              required
              minlength="6"
            />
          </div>
          <button type="submit" :disabled="loading">
            {{ loading ? 'Modification...' : 'Modifier' }}
          </button>
          <button type="button" @click="showChangePassword = false">Annuler</button>
        </form>
      </div>

      <!-- Préférences utilisateur -->
      <div class="user-preferences">
        <h3>Vos préférences</h3>
        <div class="preferences-display">
          <p><strong>Genres préférés:</strong> {{ currentUser.preferences.genres_likes.join(', ') || 'Aucun' }}</p>
          <p><strong>Genres non appréciés:</strong> {{ currentUser.preferences.genres_dislikes.join(', ') || 'Aucun' }}</p>
          <p><strong>Note minimum:</strong> {{ currentUser.preferences.rating_min }}/10</p>
          <p><strong>Services de streaming:</strong> {{ currentUser.preferences.streaming_services.join(', ') || 'Aucun' }}</p>
        </div>
      </div>

      <!-- Recommandations -->
      <div class="recommendations">
        <h3>Vos recommandations</h3>
        <button @click="loadRecommendations" :disabled="loading">
          {{ loading ? 'Chargement...' : 'Obtenir des recommandations' }}
        </button>
        
        <div v-if="recommendations.length > 0" class="recommendations-list">
          <div v-for="rec in recommendations" :key="rec.id" class="recommendation-item">
            <h4>{{ rec.title }}</h4>
            <p><strong>Note:</strong> {{ rec.rating }}/10</p>
            <p><strong>Genre:</strong> {{ rec.genre }}</p>
            <p>{{ rec.overview }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages d'erreur -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Messages de succès -->
    <div v-if="success" class="success-message">
      {{ success }}
    </div>
  </div>
</template>

<script>
export default {
  name: 'AuthComponent',
  data() {
    return {
      isAuthenticated: false,
      currentUser: {},
      showRegister: false,
      showChangePassword: false,
      loading: false,
      error: '',
      success: '',
      
      loginForm: {
        username: '',
        password: ''
      },
      
      registerForm: {
        username: '',
        password: '',
        preferences: {
          genres_likes: [],
          genres_dislikes: [],
          rating_min: 7.0,
          streaming_services: []
        }
      },
      
      changePasswordForm: {
        current_password: '',
        new_password: ''
      },
      
      availableGenres: [],
      recommendations: []
    }
  },
  
  async mounted() {
    // Vérifier si l'utilisateur est déjà connecté
    await this.checkAuthStatus();
    
    // Charger les genres disponibles
    await this.loadGenres();
  },
  
  methods: {
    async checkAuthStatus() {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const response = await fetch('/api/verify-token', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            this.isAuthenticated = true;
            this.currentUser = data.user;
          } else {
            // Token invalide
            localStorage.removeItem('auth_token');
          }
        } catch (error) {
          console.error('Erreur de vérification du token:', error);
          localStorage.removeItem('auth_token');
        }
      }
    },
    
    async login() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.loginForm)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          // Connexion réussie
          localStorage.setItem('auth_token', data.token);
          this.isAuthenticated = true;
          this.currentUser = data.user;
          this.success = 'Connexion réussie !';
          
          // Réinitialiser le formulaire
          this.loginForm = { username: '', password: '' };
        } else {
          this.error = data.error;
        }
      } catch (error) {
        this.error = 'Erreur de connexion au serveur';
        console.error('Erreur de connexion:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async register() {
      this.loading = true;
      this.error = '';
      
      try {
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.registerForm)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          // Inscription réussie
          localStorage.setItem('auth_token', data.token);
          this.isAuthenticated = true;
          this.currentUser = data.user;
          this.success = 'Inscription réussie !';
          
          // Réinitialiser le formulaire
          this.registerForm = {
            username: '',
            password: '',
            preferences: {
              genres_likes: [],
              genres_dislikes: [],
              rating_min: 7.0,
              streaming_services: []
            }
          };
        } else {
          this.error = data.error;
        }
      } catch (error) {
        this.error = 'Erreur de connexion au serveur';
        console.error('Erreur d\'inscription:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async changePassword() {
      this.loading = true;
      this.error = '';
      
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch('/api/change-password', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(this.changePasswordForm)
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.success = 'Mot de passe modifié avec succès !';
          this.showChangePassword = false;
          this.changePasswordForm = { current_password: '', new_password: '' };
        } else {
          this.error = data.error;
        }
      } catch (error) {
        this.error = 'Erreur de connexion au serveur';
        console.error('Erreur de changement de mot de passe:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async loadRecommendations() {
      this.loading = true;
      this.error = '';
      
      try {
        const token = localStorage.getItem('auth_token');
        const response = await fetch(`/api/recommendations/${this.currentUser.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        const data = await response.json();
        
        if (response.ok) {
          this.recommendations = data;
        } else {
          this.error = data.error;
        }
      } catch (error) {
        this.error = 'Erreur de chargement des recommandations';
        console.error('Erreur de recommandations:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async loadGenres() {
      try {
        const response = await fetch('/api/genres');
        const data = await response.json();
        
        if (response.ok) {
          this.availableGenres = Array.isArray(data) ? data : data.genres || [];
        } else {
          console.error('Erreur de chargement des genres:', data.error);
        }
      } catch (error) {
        console.error('Erreur de chargement des genres:', error);
      }
    },
    
    logout() {
      localStorage.removeItem('auth_token');
      this.isAuthenticated = false;
      this.currentUser = {};
      this.recommendations = [];
      this.success = 'Déconnexion réussie !';
    }
  }
}
</script>

<style scoped>
.auth-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.auth-forms {
  background: #f5f5f5;
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
}

.form-group select[multiple] {
  height: 120px;
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

button:hover {
  background: #0056b3;
}

button:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.user-dashboard {
  background: #f8f9fa;
  padding: 30px;
  border-radius: 8px;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #dee2e6;
}

.user-actions button {
  margin-left: 10px;
}

.change-password {
  background: white;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #dee2e6;
}

.user-preferences {
  background: white;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #dee2e6;
}

.preferences-display p {
  margin: 10px 0;
}

.recommendations {
  background: white;
  padding: 20px;
  border-radius: 4px;
  border: 1px solid #dee2e6;
}

.recommendations-list {
  margin-top: 20px;
}

.recommendation-item {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 15px;
  border-left: 4px solid #007bff;
}

.recommendation-item h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.existing-users-info {
  background: #e7f3ff;
  padding: 15px;
  border-radius: 4px;
  margin-top: 20px;
  border: 1px solid #b8daff;
}

.existing-users-info h3 {
  margin-top: 0;
  color: #004085;
}

.existing-users-info p {
  margin: 5px 0;
  font-family: monospace;
}

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

a {
  color: #007bff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
