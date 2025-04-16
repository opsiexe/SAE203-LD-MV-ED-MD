<template>
  <nav class="navbar">
    <div class="navbar-container">
      <a href="#" class="navbar-logo">Support</a>
      <!-- Menu utilisateur -->
      <div class="user-menu">
        <div class="avatar" @click="toggleUserMenu">
          <img v-if="userPhoto" :src="userPhoto" alt="Avatar" />
          <font-awesome-icon v-else :icon="['fas', 'circle-user']" size="lg" />
        </div>

        <div class="dropdown" v-if="isUserMenuOpen">
          <a href="/mytickets" class="menu-item">Mes tickets</a>
          <a href="/newtickets" class="menu-item">Nouveau</a>
          <a href="#" class="menu-item">Se déconnecter</a>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faBars, faXmark, faCircleUser } from '@fortawesome/free-solid-svg-icons'
import { library } from '@fortawesome/fontawesome-svg-core'

library.add(faBars, faXmark, faCircleUser)

const isMenuOpen = ref(false)
const isUserMenuOpen = ref(false)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
  isUserMenuOpen.value = false
}

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
  isMenuOpen.value = false
}
// Test temporaire — remplace par AzureAD plus tard
const userPhoto = ref(null)
</script>

<style scoped>
.navbar {
  background-color: #333;
  color: #fff;
  padding: 1rem;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 1000;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

.navbar-logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  text-decoration: none;
}

/* Hamburger */
.hamburger {
  font-size: 1.5rem;
  color: #fff;
  background: none;
  border: none;
  cursor: pointer;
}

/* Menu principal */
.navbar-menu {
  list-style: none;
  display: none;
  flex-direction: column;
  margin: 0;
  padding: 0;
  position: absolute;
  top: 100%;
  left: 0;
  background-color: #333;
  width: 100%;
}

.navbar-menu.open {
  display: flex;
}

.navbar-item {
  padding: 1rem;
  border-bottom: 1px solid #444;
}

.navbar-link {
  color: #fff;
  text-decoration: none;
  font-size: 1rem;
}

.navbar-link:hover {
  text-decoration: underline;
}

/* Menu utilisateur */
.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  margin-left: 1rem;
}

.avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #444;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar .fa-icon {
  font-size: 2rem;
  color: white;
}

.dropdown {
  position: absolute;
  top: 60px;
  right: 0;
  background-color: white;
  width: 200px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.15);
  z-index: 1001;
}

.menu-item {
  display: block;
  padding: 1rem;
  text-decoration: none;
  color: #333;
  border-bottom: 1px solid #eee;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item:hover {
  background-color: #f4f4f4;
}

/* Responsive */
@media (min-width: 768px) {
  .navbar-menu {
    display: flex !important;
    flex-direction: row;
    position: static;
    background-color: transparent;
    width: auto;
  }

  .navbar-item {
    border: none;
    padding: 0 1rem;
  }

  .dropdown {
    right: 0;
  }
}
</style>
