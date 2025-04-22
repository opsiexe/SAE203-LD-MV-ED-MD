<template>
    <div class="flex h-[calc(100vh-64px)]">
        <!-- Partie gauche -->
        <div class="w-1/2 flex items-center justify-center p-5">
            <div class="w-full max-w-sm">
                <h2 class="text-3xl font-extrabold dark:text-white mb-10">Créer un nouveau ticket</h2>
                <form @submit.prevent="createTicket" class="w-full space-y-10">
                    <div class="form-group">
                        <label for="object" class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Objet:</label>
                        <input type="text" id="object" v-model="ticket.title" required class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-3 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500" placeholder="Entrez l'objet du ticket" />
                    </div>

                    <div class="form-group">
                        <label for="description" class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Description:</label>
                        <textarea id="description" v-model="ticket.description" required rows="4" class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-3 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none" placeholder="Entrez la description du ticket"></textarea>
                    </div>

                    <div class="form-group">
                        <label for="piece-jointe" class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Pièce jointe:</label>
                        <input class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400" id="piece-jointe" type="file">
                    </div>

                    <button type="submit" class="w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-6 py-3 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Créer le ticket</button>
                </form>
            </div>
        </div>
        <div class="w-1/2">
            <!-- Vous pouvez ajouter du contenu ici si nécessaire -->
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    name: 'NewTicket',
    data() {
        return {
            ticket: {
                title: '',
                description: '',
                status: 'ouvert'
            }
        }
    },
    methods: {
        async createTicket() {
            try {
                const response = await axios.post('http://localhost:5000/api/add_ticket', this.ticket);
                console.log('Ticket créé:', response.data);
                this.ticket = {
                    title: '',
                    description: '',
                    status: 'ouvert'
                };
                // Optionnel: rediriger vers la liste des tickets
                this.$router.push('/tickets');
            } catch (error) {
                console.error('Erreur lors de la création du ticket:', error);
            }
        }
    }
}
</script>