<template>
    <div class="my-tickets">
        <h1>Mes Tickets</h1>
        <p v-if="loading">Chargement des tickets...</p>
        <p v-else-if="error">{{ error }}</p>
        <ul v-else>
            <li v-for="ticket in tickets" :key="ticket.id">
                <h3>{{ ticket.title }}</h3>
                <p>{{ ticket.description }}</p>
                <small>Créé le : {{ new Date(ticket.createdAt).toLocaleDateString() }}</small>
            </li>
        </ul>
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
    async created() {
        try {
            const response = await axios.get('/api/tickets', {
                timeout: 10000, // Timeout de 10 secondes
            });
            this.tickets = response.data;
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
    padding: 20px;
}

.my-tickets h1 {
    font-size: 24px;
    margin-bottom: 20px;
}

.my-tickets ul {
    list-style: none;
    padding: 0;
}

.my-tickets li {
    border: 1px solid #ddd;
    padding: 10px;
    margin-bottom: 10px;
    border-radius: 5px;
}

.my-tickets li h3 {
    margin: 0 0 10px;
}

.my-tickets li p {
    margin: 0 0 5px;
}

.my-tickets li small {
    color: #666;
}
</style>