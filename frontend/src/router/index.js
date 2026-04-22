import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Recommendations from '../views/Recommendations.vue';
import Profile from '../views/Profile.vue';
import store from '../store';

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: Login, meta: { guestOnly: true } },
  { path: '/recommendations', name: 'Recommendations', component: Recommendations, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
});

router.beforeEach((to, from, next) => {
  const isLoggedIn = store.getters.isLoggedIn;

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isLoggedIn) {
      next({ path: '/login', query: { redirect: to.fullPath } });
      return;
    }
  } else if (to.matched.some(record => record.meta.guestOnly)) {
    if (isLoggedIn) {
      next({ path: '/' });
      return;
    }
  }
  next();
});

export default router;
