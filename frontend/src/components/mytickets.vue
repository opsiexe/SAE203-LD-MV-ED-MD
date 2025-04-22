<template>
  <div class="max-w-2xl mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6 text-white">Mes Tickets</h1>
    <p v-if="loading" class="text-gray-500">Chargement des tickets...</p>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>
    <div v-else>
      <div v-for="ticket in tickets" :key="ticket.id"
        class="mb-6 p-5 bg-neutral-700 rounded-lg border border-gray-200 relative flex flex-col">
        <div class="mb-2 flex flex-col items-start relative">
          <h3 class="text-xl font-semibold text-white-100 mb-1">{{ ticket.objet }}</h3>
          <div class="absolute top-0 right-0 flex flex-col items-end">
            <span v-if="ticket.statut == 'ouvert'"
              class="bg-emerald-400 text-neutral-700 rounded-lg px-3 py-1 text-sm font-bold mb-2">
              {{ ticket.statut || 'Non défini' }}
            </span>
            <span v-else-if="ticket.statut == 'fini'"
              class="bg-red-500 text-white rounded-lg px-3 py-1 text-sm font-bold mb-2">
              {{ ticket.statut || 'Non défini' }}
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
    };
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
        // Retirer le ticket de la liste seulement si la suppression a réussi
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