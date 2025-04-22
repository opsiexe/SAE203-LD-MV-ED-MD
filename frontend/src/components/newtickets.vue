<template>
    <div class="flex flex-col md:flex-row min-h-[calc(100vh-64px)]">
        <!-- Formulaire centré -->
        <div class="w-full md:w-3/4 lg:w-2/3 xl:w-1/2 mx-auto flex items-center justify-center p-4 md:p-5">
            <div class="w-full max-w-md">
                <!-- Affichage des erreurs -->
                <div v-if="error"
                    class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400">
                    <div class="font-medium">Erreur lors de la création du ticket:</div>
                    <div>{{ errorMessage }}</div>
                </div>

                <h2 class="text-2xl md:text-3xl font-extrabold dark:text-white mb-4 md:mb-10">Créer un nouveau ticket
                </h2>
                <form @submit.prevent="createTicket" class="w-full space-y-4">
                    <div class="form-group">
                        <label for="object"
                            class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Objet:</label>
                        <input type="text" id="object" v-model="ticket.objet" required
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 md:p-3 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            placeholder="Entrez l'objet du ticket" />
                    </div>

                    <div class="form-group">
                        <label for="description"
                            class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Description:</label>
                        <textarea id="description" v-model="ticket.description" required rows="4"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 md:p-3 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 resize-none"
                            placeholder="Entrez la description du ticket"></textarea>
                    </div>

                    <div class="form-group">
                        <label for="email"
                            class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Email:</label>
                        <input type="email" id="email" v-model="ticket.email" required
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 md:p-3 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                            placeholder="Entrez votre email" />
                    </div>

                    <div class="form-group">
                        <label for="piece-jointe"
                            class="block text-sm font-medium text-gray-900 dark:text-white mb-2">Pièce jointe:</label>

                        <div class="relative">
                            <input
                                class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
                                id="piece-jointe" type="file" ref="fileInput" @change="handleFileChange">

                            <button type="button" v-if="selectedFile" @click="clearSelectedFile"
                                class="absolute right-2 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 focus:outline-none"
                                aria-label="Supprimer la pièce jointe">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24"
                                    stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                        d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                    </div>

                    <!-- Bouton avec état de chargement -->
                    <button type="submit" :disabled="isSubmitting"
                        class="w-full text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 md:px-6 md:py-3 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800 disabled:opacity-75">
                        <span v-if="isSubmitting" class="inline-flex items-center">
                            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg"
                                fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor"
                                    stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor"
                                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                                </path>
                            </svg>
                            Création en cours...
                        </span>
                        <span v-else>Créer le ticket</span>
                    </button>
                </form>
            </div>
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
                objet: '',
                description: '',
                email: '',
                statut: 'ouvert',
                user_id: 1 // Valeur par défaut ou à récupérer depuis l'authentification
            },
            selectedFile: null,
            isSubmitting: false,
            error: false,
            errorMessage: ''
        }
    },
    methods: {
        handleFileChange(event) {
            this.selectedFile = event.target.files[0] || null;
        },
        clearSelectedFile() {
            this.selectedFile = null;
            // Réinitialiser l'input file
            this.$refs.fileInput.value = '';
        },
        async createTicket() {
            // Réinitialiser l'état d'erreur
            this.error = false;
            this.errorMessage = '';

            // Éviter les soumissions multiples
            if (this.isSubmitting) return;
            this.isSubmitting = true;

            try {
                const formData = new FormData();
                formData.append('objet', this.ticket.objet);
                formData.append('description', this.ticket.description);
                formData.append('email', this.ticket.email);
                formData.append('statut', this.ticket.statut);
                formData.append('user_id', this.ticket.user_id);

                // Dates actuelles
                const now = new Date().toISOString();
                formData.append('date_creation', now);
                formData.append('date_modification', '');
                formData.append('date_resolution', '');

                // Ajout de la pièce jointe si elle existe
                if (this.selectedFile) {
                    formData.append('piece_jointe', this.selectedFile.name);
                    formData.append('file', this.selectedFile);
                } else {
                    formData.append('piece_jointe', '');
                }

                // Pour le debug - log des données envoyées
                console.log('Envoi des données:', Object.fromEntries(formData.entries()));

                const response = await axios.post('http://localhost:5000/api/add_ticket', formData);

                console.log('Ticket créé:', response.data);

                // Réinitialiser les champs
                this.ticket = {
                    objet: '',
                    description: '',
                    email: '',
                    statut: 'ouvert',
                    user_id: 1
                };
                this.clearSelectedFile();

                // Redirection vers la liste des tickets
                this.$router.push('/mytickets');
            } catch (error) {
                console.error('Erreur lors de la création du ticket:', error);

                // Afficher le message d'erreur
                this.error = true;
                if (error.response) {
                    // La requête a été faite et le serveur a répondu avec un code d'état
                    this.errorMessage = `Erreur du serveur (${error.response.status}): ${error.response.data?.message || 'Détails non disponibles'}`;
                    console.log('Données d\'erreur:', error.response.data);
                } else if (error.request) {
                    // La requête a été faite mais aucune réponse n'a été reçue
                    this.errorMessage = 'Aucune réponse reçue du serveur. Vérifiez que le backend est en cours d\'exécution.';
                } else {
                    // Une erreur s'est produite lors de la configuration de la requête
                    this.errorMessage = `Erreur de configuration: ${error.message}`;
                }
            } finally {
                this.isSubmitting = false;
            }
        }
    }
}
</script>