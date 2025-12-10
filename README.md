# Basketball DB - Interface de Gestion

Une application web Flask pour gérer et visualiser une base de données de basketball (PostgreSQL). Elle offre un tableau de bord interactif, une gestion complète des joueurs et des matchs, ainsi que des outils d'administration.

## Fonctionnalités Principales

### 📊 Tableau de Bord Interactif
- **Indicateurs clés** : Nombre total de joueurs, clubs, matchs et ligues.
- **Graphiques** :
    - Répartition des joueurs par nationalité (Doughnut Chart).
    - Top 5 des meilleurs marqueurs (Bar Chart).

### 🏀 Gestion des Joueurs
- **Liste filtrable** : Recherche par nom, filtrage par club, nationalité et continent.
- **Profil Public** : Page détaillée pour chaque joueur avec ses informations personnelles et ses **statistiques de carrière** calculées (Points, PPG, RPG, APG, Contres).
- **Administration** : Création et modification de fiches joueurs (réservé aux rôles `admin` et `staff`).

### 🏟️ Matchs et Statistiques
- **Liste des matchs** : Filtrage par saison, type de jeu et ligue.
- **Fiche de Match (Box Score)** : Vue détaillée d'un match avec le tableau complet des statistiques de chaque joueur (Points, Rebonds, Passes, etc.).

### 🛠️ Outils d'Administration
- **Exécuteur SQL** : Interface pour exécuter des requêtes SQL arbitraires ou prédéfinies directement depuis le navigateur (réservé au rôle `admin`).

## Installation et Lancement

### Prérequis
- Python 3.10+
- PostgreSQL avec la base de données `basketball` initialisée.

### Configuration
1.  Créer un environnement virtuel :
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
2.  Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
3.  Configurer les variables d'environnement (optionnel, fichier `.env`) :
    - `DATABASE_URL` : URL de connexion PostgreSQL (défaut : `postgresql+psycopg2://postgres:secret@localhost:5432/basketball`)
    - `APP_SECRET_KEY` : Clé secrète Flask.

### Démarrage
```bash
python app.py
```
L'application sera accessible sur `http://localhost:5000`.

## Rôles et Comptes de Démonstration

| Rôle   | Identifiant | Mot de passe | Permissions |
| :---   | :---        | :---         | :--- |
| **Admin**  | `admin`     | `admin123`   | Accès complet (CRUD Joueurs, SQL Runner). |
| **Staff**  | `staff`     | `staff123`   | Gestion des joueurs (Création/Édition). |
| **Viewer** | `viewer`    | `viewer123`  | Lecture seule (Tableau de bord, Profils, Matchs). |

## Structure du Projet

- `app.py` : Application Flask principale (Routes, Modèles, Logique).
- `templates/` : Gabarits HTML (Jinja2).
- `static/` : Fichiers CSS et images.
- `CreateTables.sql` : Script de création de la base de données.
- `seed_db.py` : Script de peuplement de la base avec des données de test (Faker).
