# 🎫 Application de Gestion de Tickets

Projet fullstack de gestion de tickets de support avec :
- 🎨 Frontend : Vue.js
- 🧠 Backend : Flask
- 🗃️ Base de données : PostgreSQL via Docker
- 💻 Environnement de dev : GitHub Codespaces

---

## 🚀 Lancement rapide

### 1. Cloner le dépôt sur GitHub Codespaces

Clique sur **"Code > Codespaces > Create codespace on main"** pour lancer ton espace de développement dans le cloud.

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

Sur l'editeur web codespace, a coter du terminal tu devrait un onglet `port` clique dessu tu devrait avoir 3 port d'ouvert :

| Port | Fonction             |
|------|----------------------|
| 5000 | Application Backend  |
| 5173 | Application Frontend |
| 5433 | Serveur PostgreSQL   |

Vous aurez juste a cliquer sur le lien.

**⚠️Les lien sont disponible que sur l'interface web du Codespace sinon c'est des adresses localhost qui ne vont bien sur pas fonctionner !**
