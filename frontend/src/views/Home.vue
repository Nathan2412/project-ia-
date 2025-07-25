<template>
  <div class="home">
    <div class="hero-section py-5 text-center">
      <h1 class="display-4 mb-3">Système de Recommandation de Films et Séries</h1>
      <p class="lead mb-4">Découvrez des films et séries parfaitement adaptés à vos goûts</p>
      <router-link to="/login" class="btn btn-primary btn-lg" v-if="!isLoggedIn">Commencer</router-link>
      <router-link to="/recommendations" class="btn btn-primary btn-lg" v-else>Voir mes recommandations</router-link>
    </div>

    <div class="row mt-5">
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Recommandations Personnalisées</h5>
            <p class="card-text">Notre système analyse vos préférences pour vous recommander des films et séries qui vous correspondent.</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Recherche par Service de Streaming</h5>
            <p class="card-text">Filtrez les recommandations selon les plateformes auxquelles vous êtes abonné(e).</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="card-title">Profil Personnalisable</h5>
            <p class="card-text">Mettez à jour vos préférences à tout moment pour affiner les recommandations.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  computed: {
    isLoggedIn() {
      return this.$store.state.currentUser !== null;
    }
  }
}
</script>
