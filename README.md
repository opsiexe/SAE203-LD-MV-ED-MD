# 🎫 Application de Gestion de Tickets

Projet fullstack de gestion de tickets de support avec :
- 🎨 Frontend : Vue.js
- 🧠 Backend : Flask
- 🗃️ Base de données : PostgreSQL via Docker
- 💻 Environnement de dev : GitHub Codespaces

---

## 🚀 Lancement rapide

### 1. Lancer le Codespace (obligatoire)

Clique sur **"Code > Codespaces > Create codespace on main"** pour lancer ton espace de développement dans le cloud. Une fois dans le codespace lance cette commande pour démarer le frontend : 

```bash
nohup npm run dev --prefix frontend &
```

### 2. Verifier que le docker est lancer

Ouvre un terminal si ce n'est pas deja fait et fait la commande :

```bash
docker ps
```

tu devrait avoir une liste des docker lancer recupère le nom du docker Postgre c'est généralement la dernière colonne

### 3. Essaie de te connecter a ta base de donnée

Toujours dans le terminal execute cette commande :

```bash
docker exec -it pg-sae203 psql -U postgres -d supportdb
```
tu devrait avoir accès a ta base de donnée

### 4. Accéder a la prévisualisation

Sur VScode, à coter du terminal tu devrait voir un onglet `port` clique dessus tu devrait avoir 3 port d'ouvert :

| Port | Fonction             |
|------|----------------------|
| 5000 | Application Backend  |
| 5173 | Application Frontend |
| 5433 | Serveur PostgreSQL   |

Vous aurez juste a cliquer un des port pour acceder a la prévisualisation 

**⚠️Les lien sont disponible que sur l'interface web du Codespace sinon c'est des adresses localhost qui ne vont bien sur pas fonctionner !**

---
## 🧠 Structure et fonctionnement du projet

Ce projet est une application de gestion de tickets de support divisée en deux interfaces distinctes :

- 🎨 Frontend (Vue.js) – pour les utilisateurs finaux qui veulent envoyer un ticket
- 🧠 Backend (Flask) – pour les agents de support qui peuvent voir, gérer et répondre aux tickets

### 🔙 Backend – Interface Support (Flask)

📁 Dossier : `backend/src/`

Cette partie est utilisée par les agents de support pour :

- Voir tous les tickets reçus

- Répondre à un ticket

- Chnager le statut d'un ticket

- Envoyer une réponse par email

📌 Fichiers clés :

| Fichier            | Rôle                                                                                                     |
|--------------------|----------------------------------------------------------------------------------------------------------|
| `app.py`           | Point d’entrée de l’application Flask                                                                    |
| `templates/`       | Contient les templates HTML du backend                                                                   |
| `static/`          | Pour les fichier statiques (CSS, JS, images) liés à Flask                                                |
| `init_db.py`       | Script d'initialisation de la base (création des tables)(ne pas toucher sauf cas speciaux)                                 |
| `requirements.txt` | Liste des dépendances Python du backend pour l'installation (ne pas toucher sauf ajout d'une dépendance) |

✅ Pour modifier cette interface :
- Modifier l’UI ➜ `templates/*.html`
- Modifier la logique (filtrage, envoi email, etc.) ➜ `app.py`
- Ajouter une table ou changer une structure ➜ `init_db.py` + relancer (prevenir en cas de modifications)

### 🎨 Frontend – Formulaire Utilisateur (Vue.js)

📁 Dossier : `frontend/`

Cette partie est utilisée par les agents de support pour :

- Voir tous les tickets reçus

- Répondre à un ticket

- Changer le status d'un ticket

- Envoyer une réponse par email

📌 Fichiers clés :

| Fichier/Dossier               | Rôle |
|-------------------------------|------|
| `src/App.vue`                 | Composant principal |
| `src/components/`             | Composants UI (formulaire de ticket, alertes, etc.) |
| `src/assets/`                 | Images, styles, icônes |
| `src/main.js`                 | Point d’entrée Vue |
| `public/index.html`           | Base HTML injectée par Vite |

#### ✅ Pour modifier cette interface :
- Modifier l’apparence ➜ `src/components/*.vue`

---

## 🔗 Communication entre les deux

- Le **frontend** envoie les tickets via `POST` à une route Flask (souvent `/create` ou `/submit`)
- Le **backend** traite la requête, enregistre dans PostgreSQL
- Les agents utilisent l’interface Flask pour gérer les réponses, consulter l’état, etc.