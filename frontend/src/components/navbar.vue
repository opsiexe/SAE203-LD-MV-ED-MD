<template>
  <nav class="navbar top-0 left-0 w-full shadow z-50">
    <div class="navbar-container flex items-center justify-between w-full max-w-screen mx-auto p-4">
      <!-- Lien "Support" aligné à gauche -->
      <a href="/" class="text-lg font-semibold">
        Support
      </a>

      <!-- Avatar aligné à droite -->
      <div class="relative">
        <button type="button" class="inline-flex items-center p-0.5 text-sm text-gray-500 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200" @click="toggleDropdown">          
          <template v-if="userPhoto">
            <img 
              class="w-10 h-10 rounded-full cursor-pointer"
              :src="userPhoto"
              alt="Photo de profil"
            />
          </template>
          <template v-else>
            <FontAwesomeIcon 
              icon="circle-user" 
              class="text-gray-400 fa-3x"
            />
          </template>
        </button>

        <div v-if="isDropdownOpen">
          <div id="userDropdown" class="absolute right-0 mt-2 z-10 bg-white rounded-lg shadow w-44 dark:bg-gray-700">
            <!-- User Info Section -->
            <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-600">
              <div class="text-sm font-semibold text-gray-900 dark:text-white">Bonnie Green</div>
              <div class="text-sm font-medium text-gray-500 truncate dark:text-gray-400">name@flowbite.com</div>
            </div>

            <!-- Navigation Links -->
            <ul class="py-2 text-sm text-gray-700 dark:text-gray-200">
              <li>
                <a href="/mytickets" class="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Mes tickets</a>
              </li>
              <li>
                <a href="/newtickets" class="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Nouveau ticket</a>
              </li>
              <li>
                <a href="/profile" class="block px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 dark:hover:text-white">Mon profil</a>
              </li>
            </ul>

            <!-- Logout Section -->
            <div class="py-2 border-t border-gray-200 dark:border-gray-600">
              <a href="/logout" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 dark:text-gray-200 dark:hover:text-white">
                Déconnexion
              </a>
            </div>
          </div>
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

// Vous pourrez plus tard remplacer ceci par la vraie photo de l'utilisateur
const userPhoto = ref(null) // null pour afficher l'icône, mettre l'URL pour afficher la photo

const isDropdownOpen = ref(false)

// Fonction pour basculer l'état du dropdown
const toggleDropdown = () => {
  isDropdownOpen.value = !isDropdownOpen.value
}
</script>