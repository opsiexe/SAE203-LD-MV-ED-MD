<template>
  <div class="max-w-2xl mx-auto p-6">
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6 gap-4">
      <div>
        <div class="flex items-center">
          <h1 class="text-3xl font-bold text-white mr-2">Mes Tickets</h1>
          <!-- Bouton refresh à droite du titre, plus petit et sans background -->
          <button
            class="flex items-center justify-center w-7 h-7 rounded-full hover:bg-gray-700/30 transition focus:outline-none ml-1"
            style="background: none;" @click="fetchTickets" :disabled="loading" aria-label="Rafraîchir">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-white" viewBox="0 0 512 512"
              fill="currentColor">
              <path
                d="M500.3 34.9l-22.2-22.2c-9.4-9.4-24.6-9.4-33.9 0l-67.1 67.1C342.7 60.7 300.7 48 256 48 141.1 48 48 141.1 48 256c0 114.9 93.1 208 208 208 100.5 0 183.1-70.8 204.2-164.2 2.9-12.5-7.1-24.2-20-24.2h-35.6c-9.4 0-17.6 6.5-19.7 15.7C372.6 372.2 318.7 416 256 416c-88.2 0-160-71.8-160-160s71.8-160 160-160c43.2 0 82.5 16.6 112.4 43.6l-74.1 74.1c-15.1 15.1-4.4 41 17 41h144c13.3 0 24-10.7 24-24V51.9c0-21.4-25.9-32.1-41-17z" />
            </svg>
          </button>
        </div>
        <span class="text-xs text-blue-300 underline cursor-pointer block mt-1" @click="showAll = !showAll">
          {{ showAll ? 'Masquer les tickets clôturés' : 'Afficher tous les tickets' }}
        </span>
      </div>
      <div>
        <div class="flex items-center gap-2 mt-2 sm:mt-0">
          <router-link to="/newtickets">
            <button class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition">
              Nouveau ticket
            </button>
          </router-link>
          <router-link to="/logout">
            <button class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition">
              Deconnexion
            </button>
          </router-link>
        </div>
      </div>
    </div>
    <p v-if="loading" class="text-gray-500">Chargement des tickets...</p>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>
    <div v-else>
      <div v-for="ticket in filteredTickets" :key="ticket.id"
        class="mb-6 p-5 bg-neutral-700 rounded-lg border border-gray-200 relative flex flex-col">
        <div class="mb-2 flex flex-col items-start relative">
          <h3 class="text-xl font-semibold text-white-100 mb-1">{{ ticket.objet }}</h3>
          <div class="absolute top-0 right-0 flex flex-col items-end">
            <span v-if="ticket.statut == 'new'"
              class="bg-blue-600 text-white rounded-lg px-3 py-1 text-sm font-bold mb-2">
              {{ 'Nouveau' || 'Non défini' }}
            </span>
            <span v-else-if="ticket.statut == 'pending'"
              class="bg-orange-600 text-white rounded-lg px-3 py-1 text-sm font-bold mb-2">
              {{ 'En cours' || 'Non défini' }}
            </span>
            <span v-else-if="ticket.status == 'assigned'"
              class="bg-purple-600 text-white rounded-lg px-3 py-1 text-sm font-bold mb-2">
              {{ 'Assigné' || 'Non défini' }}
            </span>
            <span v-else-if="ticket.status == 'resolved'"
              class="bg-green-600 text-white rounded-lg px-3 py-1 text-sm font-bold mb-2">
              {{ 'Résolu' || 'Non défini' }}
            </span>
            <span v-else-if="ticket.status == 'closed'"
              class="bg-gray-600 text-white rounded-lg px-3 py-1 text-sm font-bold mb-2">
              {{ 'Clôturé' || 'Non défini' }}
            </span>
            <span v-else class="bg-gray-400 text-white rounded-lg px-3 py-1 text-sm font-bold mb-2">
              {{ ticket.statut || 'Non défini' }}
            </span>
            <button class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition"
              @click="deleteTicket(ticket.id)">
              Supprimer
            </button>
          </div>
        </div>
        <p class="text-white-700 mb-2">{{ ticket.description }}</p>
        <p>
          <span class="font-medium text-white-600">Date: </span>
          <span class="text-white-800">{{ formatDate(ticket.date_creation) }}</span>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'MyTickets',
  data() {
    return {
      tickets: [],
      loading: true,
      error: null,
      showAll: false,
    };
  },
  computed: {
    filteredTickets() {
      return this.showAll
        ? this.tickets
        : this.tickets.filter(ticket =>
          (ticket.statut || ticket.status) !== 'closed'
        );
    },
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return 'Non spécifiée';
      const date = new Date(dateStr);
      return date.toLocaleString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    },
    async deleteTicket(id) {
      try {
        await axios.post(`http://localhost:5000/api/delete_ticket/${id}`, null, {
          timeout: 10000,
        });
        this.tickets = this.tickets.filter(ticket => ticket.id !== id);
      } catch (error) {
        this.error = 'Erreur lors de la suppression du ticket';
      }
    },
    async fetchTickets() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('http://localhost:5000/api/gettickets', {
          timeout: 10000,
        });
        this.tickets = response.data.filter(ticket => ticket.user_id === 1);
      } catch (error) {
        this.error = 'Erreur lors de la récupération des tickets';
      } finally {
        this.loading = false;
      }
    }
  },
  async created() {
    await this.fetchTickets();
  }
};
</script>