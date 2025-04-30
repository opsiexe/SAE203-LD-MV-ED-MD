<template>
  <nav class="navbar top-0 left-0 w-full shadow z-50">
    <div class="navbar-container flex items-center justify-between w-full max-w-screen mx-auto p-4">
      <!-- Lien "Support" aligné à gauche -->
      <a href="/" class="text-lg font-semibold">
        Support
      </a>
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