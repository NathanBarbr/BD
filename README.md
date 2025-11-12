# Interface applicative pour la base PostgreSQL

Cette application Flask/SQLAlchemy fournit une interface web simple (tableau de bord, gestion des joueurs, visualisation des matchs) connectee a la base `basketball` creee par `CreateTables.sql`. Elle ajoute une couche d'authentification et de droits (admin, staff, viewer).

## Prerequis

- Python 3.10+
- PostgreSQL en cours d'execution avec la base `basketball` (voir `CreateTables.sql`)

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Configuration

Les variables suivantes peuvent etre definies dans un fichier `.env` ou dans l'environnement systeme :

- `DATABASE_URL` : chaine SQLAlchemy vers votre instance (defaut `postgresql+psycopg2://postgres:secret@localhost:5432/basketball`).
- `APP_SECRET_KEY` : cle Flask utilisee pour signer les sessions (defaut de developpement `dev-change-me`).

## Lancement

```bash
$env:FLASK_APP = "app"   # PowerShell
flask run --debug
```

L'interface est ensuite accessible sur http://localhost:5000.

## Comptes de demonstration

| Utilisateur | Mot de passe | Role   | Capacites principales                |
|-------------|--------------|--------|--------------------------------------|
| admin       | admin123     | admin  | Lecture + creation/modification      |
| staff       | staff123     | staff  | Meme droits que admin sur les joueurs|
| viewer      | viewer123    | viewer | Lecture seule                        |

> Pour une integration reelle, remplacez ces comptes statiques par une table utilisateur et un stockage de mots de passe haches.

## Fonctionnalites clefs

- **Tableau de bord** : indicateurs (joueurs, clubs, matchs, ligues), top scoreurs, prochains matchs.
- **Gestion des joueurs** : recherche textuelle, filtre par club, creation/edition conditionnee par le role.
- **Matchs** : filtres par saison/type/ligue et affichage des participants avec leurs scores.

## Tests rapides

1. Charger vos donnees (scripts `CreateTables.sql` + inserts).
2. Lancer l'appli puis se connecter avec `admin/admin123`.
3. Ajouter un joueur et verifier son apparition dans la liste.
4. Consulter `Matchs` pour valider la resolution des participants (clubs/equipes nationales).

N'hesitez pas a adapter les gabarits Jinja (`templates/`) ou le style (`static/styles.css`) pour coller a votre charte.
