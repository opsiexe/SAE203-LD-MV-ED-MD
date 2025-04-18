<template>
  <nav class="navbar fixed top-0 left-0 w-full shadow z-50">
    <div class="navbar-container flex items-center justify-between w-full max-w-screen mx-auto p-4">
      <!-- Lien "Support" aligné à gauche -->
      <a href="/" class="text-lg font-semibold">
        Support
      </a>

      <!-- Avatar aligné à droite -->
      <div class="relative">
        <button
          type="button"
          class="inline-flex items-center p-2 text-sm text-gray-500 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200"
          @click="toggleDropdown"
        >
          <span class="sr-only">Ouvrir le menu utilisateur</span>
          <div class="avatar">
            <img v-if="userPhoto" :src="userPhoto" alt="Avatar" class="w-8 h-8 rounded-full" />
            <font-awesome-icon v-else :icon="['fas', 'circle-user']" size="lg" />
          </div>
        </button>

        <!-- Dropdown -->
        <div
          v-if="isDropdownOpen"
          class="absolute right-0 mt-2 z-10 font-normal bg-white divide-y divide-gray-100 rounded-lg shadow w-44 dark:bg-gray-700 dark:divide-gray-600"
        >
          <ul class="py-2 text-sm text-gray-700 dark:text-gray-200">
            <li>
              <a
                href="#"
                class="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
              >
                Mon compte
              </a>
            </li>
            <li>
              <a
                href="/mytickets"
                class="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
              >
                Mes tickets
              </a>
            </li>
            <li>
              <a
                href="#"
                class="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white"
              >
                Déconnexion
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faCircleUser } from '@fortawesome/free-solid-svg-icons'
import { library } from '@fortawesome/fontawesome-svg-core'

library.add(faCircleUser)

// Test temporaire — remplace par AzureAD plus tard
const userPhoto = ref(null)
const isDropdownOpen = ref(false)

// Fonction pour basculer l'état du dropdown
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}
</script>