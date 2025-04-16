<template>
  <div class="my-tickets">
    <h1>Mes Tickets</h1>
    <p v-if="loading">Chargement des tickets...</p>
    <p v-else-if="error">{{ error }}</p>
    <div v-else class="tickets-grid">
      <div v-for="ticket in tickets" :key="ticket.id" class="ticket-item">
        <h3>{{ ticket.objet }}</h3>
        <p>{{ ticket.description }}</p>
        <p><strong>Statut:</strong> {{ ticket.statut || 'Non défini' }}</p>
        <p>
          <strong>Date:</strong>
          {{ formatDate(ticket.date_creation) }}
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
  },
  async created() {
    try {
      console.log('Fetching tickets...');
      const response = await axios.get('http://localhost:5000/api/tickets', {
        timeout: 10000,
      });
      this.tickets = response.data.filter(ticket => ticket.user_id === 1);
    } catch (error) {
      this.error = 'Erreur lors de la récupération des tickets';
      console.error(error);
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
.my-tickets {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 20px;
  margin: 0;
  margin-top: 60px; /* Ajoute un espace pour compenser la hauteur de la navbar */
  height: calc(100vh - 60px); /* Ajuste la hauteur pour exclure la navbar */
  width: 100%; /* Occupe toute la largeur de la page */
  box-sizing: border-box;
}

.my-tickets h1 {
  font-size: 32px;
  margin-bottom: 20px;
  text-align: center;
  width: 100%; /* S'assure que le titre est centré horizontalement */
}

.tickets-grid {
  display: flex;
  flex-direction: column; /* Affiche les tickets en colonne */
  gap: 20px;
  width: 100%; /* Prend toute la largeur disponible */
}

.ticket-item {
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 8px;
  background-color: #f9f9f9;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%; /* Chaque ticket prend toute la largeur */
}

.ticket-item h3 {
  margin: 0 0 10px;
}

.ticket-item p {
  margin: 0 0 5px;
}
</style>
