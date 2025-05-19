<template>
  <div class="max-w-2xl mx-auto p-6">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-3xl font-bold text-white">Mes Tickets</h1>
        <span class="text-xs text-blue-300 underline cursor-pointer block mt-1" @click="showAll = !showAll">
          {{ showAll ? 'Masquer les tickets clôturés' : 'Afficher tous les tickets' }}
        </span>
      </div>
      <div>
        <router-link to="/newtickets">
          <button class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition">
            Nouveau ticket
          </button>
        </router-link>
        <router-link to="/logout" class="ml-2">
          <button class="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded-lg transition">
            Deconnexion
          </button>
        </router-link>
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
      showAll: false, // Ajouté
    };
  },
  computed: {
    filteredTickets() {
      // Affiche tous les tickets si showAll, sinon filtre les "closed"
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
    }
  },
  async created() {
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
};
</script>