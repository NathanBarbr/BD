import os
from datetime import date, datetime
from functools import wraps

from dotenv import load_dotenv
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, func
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DEFAULT_DB_URL = "postgresql+psycopg2://postgres:secret@localhost:5432/basketball"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true"
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY", "dev-change-me")

db = SQLAlchemy(app)


USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "staff": {"password": "staff123", "role": "staff"},
    "viewer": {"password": "viewer123", "role": "viewer"},
}

ROLE_PERMISSIONS = {
    "admin": {"can_edit_players": True},
    "staff": {"can_edit_players": True},
    "viewer": {"can_edit_players": False},
}


class League(db.Model):
    __tablename__ = "league"

    id_lea = db.Column(db.Integer, primary_key=True)
    league_id = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(50), nullable=False)


class Championship(db.Model):
    __tablename__ = "championship"

    id_cha = db.Column(db.Integer, primary_key=True)
    championship_id = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(50), nullable=False)


class Club(db.Model):
    __tablename__ = "clubs"

    id_clu = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)

    players = db.relationship("Player", back_populates="club")


class NationalTeam(db.Model):
    __tablename__ = "national_team"

    id_nat = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    confederation = db.Column(db.String(100))


class Player(db.Model):
    __tablename__ = "player"

    id_pla = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    height = db.Column(db.Numeric(4, 2))
    citizenship = db.Column(db.String(50))
    current_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id_clu"))

    club = db.relationship("Club", back_populates="players", lazy="joined")


class Game(db.Model):
    __tablename__ = "game"

    id_gam = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.String(10), nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    game_type = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(50))
    id_lea = db.Column(db.Integer, db.ForeignKey("league.id_lea"))
    id_cha = db.Column(db.Integer, db.ForeignKey("championship.id_cha"))

    league = db.relationship("League", lazy="joined")
    championship = db.relationship("Championship", lazy="joined")
    participants = db.relationship(
        "GameParticipant", back_populates="game", lazy="joined"
    )


class GameParticipant(db.Model):
    __tablename__ = "game_participant"

    id_gam = db.Column(db.Integer, db.ForeignKey("game.id_gam"), primary_key=True)
    participant_id = db.Column(db.Integer, primary_key=True)
    participant_type = db.Column(db.String(20), primary_key=True)
    score = db.Column(db.Integer, default=0)
    role = db.Column(db.String(10))

    game = db.relationship("Game", back_populates="participants")


class PlayerGameStats(db.Model):
    __tablename__ = "player_game_stats"

    id_gam = db.Column(db.Integer, db.ForeignKey("game.id_gam"), primary_key=True)
    id_pla = db.Column(db.Integer, db.ForeignKey("player.id_pla"), primary_key=True)
    id_stat = db.Column(db.Integer)
    points_2pts_made = db.Column(db.Integer, default=0)
    points_2pts_attempted = db.Column(db.Integer, default=0)
    points_3pts_made = db.Column(db.Integer, default=0)
    points_3pts_attempted = db.Column(db.Integer, default=0)
    free_throws_made = db.Column(db.Integer, default=0)
    free_throws_attempted = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    rebounds = db.Column(db.Integer, default=0)
    blocks = db.Column(db.Integer, default=0)

    player = db.relationship("Player", lazy="joined")
    game = db.relationship("Game", lazy="joined")


# --- Helpers -----------------------------------------------------------------


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapper


def role_required(*accepted_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            user = session.get("user")
            if not user or user["role"] not in accepted_roles:
                flash("Vous n'avez pas les droits necessaires pour cette action.", "error")
                return redirect(url_for("dashboard"))
            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def current_user():
    return session.get("user")


def current_permissions():
    user = current_user()
    if not user:
        return {}
    return ROLE_PERMISSIONS.get(user["role"], {})


def attach_participant_names(games):
    club_ids = set()
    team_ids = set()
    for game in games:
        for participant in game.participants:
            if participant.participant_type.lower() == "club":
                club_ids.add(participant.participant_id)
            elif participant.participant_type.lower() == "national":
                team_ids.add(participant.participant_id)

    clubs = {}
    teams = {}
    if club_ids:
        clubs = {
            club.id_clu: club.name
            for club in Club.query.filter(Club.id_clu.in_(club_ids)).all()
        }
    if team_ids:
        teams = {
            team.id_nat: team.country
            for team in NationalTeam.query.filter(NationalTeam.id_nat.in_(team_ids)).all()
        }

    for game in games:
        for participant in game.participants:
            if participant.participant_type.lower() == "club":
                participant.display_name = clubs.get(
                    participant.participant_id, f"Club #{participant.participant_id}"
                )
            elif participant.participant_type.lower() == "national":
                participant.display_name = teams.get(
                    participant.participant_id, f"Selection #{participant.participant_id}"
                )
            else:
                participant.display_name = f"Participant #{participant.participant_id}"


@app.context_processor
def inject_globals():
    return {
        "current_user": current_user(),
        "permissions": current_permissions(),
    }


# --- Auth --------------------------------------------------------------------


@app.route("/", methods=["GET"])
def home():
    if current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = USERS.get(username)
        if user and password == user["password"]:
            session["user"] = {
                "username": username,
                "role": user["role"],
            }
            flash("Connexion reussie", "info")
            return redirect(url_for("dashboard"))
        flash("Identifiants invalides", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# --- Dashboard ---------------------------------------------------------------


@app.route("/dashboard")
@login_required
def dashboard():
    total_players = Player.query.count()
    total_games = Game.query.count()
    total_clubs = Club.query.count()
    
    # Chart 1: Players by Citizenship
    citizenship_data = db.session.query(Player.citizenship, func.count(Player.id_pla)).group_by(Player.citizenship).all()
    citizenship_labels = [c[0] for c in citizenship_data if c[0]]
    citizenship_values = [c[1] for c in citizenship_data if c[0]]
    
    # Chart 2: Top 5 Scorers (Calculated from stats)
    top_scorers_query = db.session.query(
        Player.name,
        func.sum(PlayerGameStats.points_2pts_made * 2 + PlayerGameStats.points_3pts_made * 3 + PlayerGameStats.free_throws_made).label('total_points')
    ).join(PlayerGameStats, Player.id_pla == PlayerGameStats.id_pla).group_by(Player.name).order_by(desc('total_points')).limit(5).all()
    
    scorer_labels = [s[0] for s in top_scorers_query]
    scorer_values = [int(s[1]) for s in top_scorers_query]

    return render_template(
        "dashboard.html",
        total_players=total_players,
        total_games=total_games,
        total_clubs=total_clubs,
        active="dashboard",
        chart_data={
            "citizenship_labels": citizenship_labels,
            "citizenship_values": citizenship_values,
            "scorer_labels": scorer_labels,
            "scorer_values": scorer_values
        }
    )


@app.route("/players")
@login_required
def players():
    q = request.args.get("q", "").strip()
    club_id = request.args.get("club")
    club_id_int = int(club_id) if club_id else None
    citizenship = request.args.get("citizenship", "").strip()
    continent = request.args.get("continent", "").strip()

    query = Player.query.order_by(Player.name.asc())
    if q:
        query = query.filter(Player.name.ilike(f"%{q}%"))
    if club_id_int:
        query = query.filter(Player.current_club_id == club_id_int)
    if citizenship:
        query = query.filter(Player.citizenship == citizenship)
    if continent:
        query = query.join(NationalTeam, Player.citizenship == NationalTeam.country).filter(NationalTeam.confederation == continent)

    players_list = query.limit(200).all()
    clubs = Club.query.order_by(Club.name.asc()).all()
    
    # Get unique confederations (continents)
    continents = db.session.query(NationalTeam.confederation).distinct().order_by(NationalTeam.confederation.asc()).all()
    continents = [c[0] for c in continents if c[0]]

    # Get unique citizenships
    citizenships = db.session.query(Player.citizenship).distinct().order_by(Player.citizenship.asc()).all()
    citizenships = [c[0] for c in citizenships if c[0]]

    return render_template(
        "players.html",
        players=players_list,
        clubs=clubs,
        continents=continents,
        citizenships=citizenships,
        filters={"q": q, "club": club_id, "citizenship": citizenship, "continent": continent},
        active="players",
    )


@app.route("/players/<int:player_id>")
@login_required
def player_profile(player_id):
    player = Player.query.get_or_404(player_id)
    
    # Fetch all game stats for this player
    stats = PlayerGameStats.query.filter_by(id_pla=player_id).all()
    
    # Calculate career stats
    games_played = len(stats)
    total_points = 0
    total_rebounds = 0
    total_assists = 0
    total_blocks = 0
    
    for stat in stats:
        points = (stat.points_2pts_made * 2) + (stat.points_3pts_made * 3) + stat.free_throws_made
        total_points += points
        total_rebounds += stat.rebounds
        total_assists += stat.assists
        total_blocks += stat.blocks
        
    ppg = round(total_points / games_played, 1) if games_played > 0 else 0
    rpg = round(total_rebounds / games_played, 1) if games_played > 0 else 0
    apg = round(total_assists / games_played, 1) if games_played > 0 else 0

    career_stats = {
        "games_played": games_played,
        "total_points": total_points,
        "ppg": ppg,
        "rpg": rpg,
        "apg": apg,
        "total_blocks": total_blocks
    }

    return render_template("player_profile.html", player=player, stats=career_stats)


@app.route("/players/new", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def create_player():
    return _persist_player()


@app.route("/players/<int:player_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin", "staff")
def edit_player(player_id):
    player = Player.query.get_or_404(player_id)
    return _persist_player(player)


def _persist_player(player=None):
    clubs = Club.query.order_by(Club.name.asc()).all()
    is_edit = player is not None

    if request.method == "POST":
        try:
            target = player or Player()
            target.player_id = request.form["player_id"].strip()
            target.name = request.form["name"].strip()
            dob_value = request.form.get("date_of_birth")
            if dob_value:
                target.date_of_birth = datetime.strptime(dob_value, "%Y-%m-%d").date()
            else:
                flash("La date de naissance est obligatoire.", "error")
                return render_template(
                    "player_form.html",
                    player=player,
                    clubs=clubs,
                    form_data=_player_form_defaults(player),
                    active="players",
                )
            height = request.form.get("height")
            target.height = float(height) if height else None
            target.citizenship = request.form.get("citizenship") or None
            club_value = request.form.get("club_id")
            target.current_club_id = int(club_value) if club_value else None

            if not is_edit:
                db.session.add(target)
            db.session.commit()
            flash("Joueur enregistre", "info")
            return redirect(url_for("players"))
        except (ValueError, SQLAlchemyError) as exc:
            db.session.rollback()
            flash(f"Impossible d'enregistrer le joueur ({exc}).", "error")

    return render_template(
        "player_form.html",
        player=player,
        clubs=clubs,
        form_data=_player_form_defaults(player),
        active="players",
    )


def _player_form_defaults(player=None):
    if not player:
        return {
            "player_id": "",
            "name": "",
            "date_of_birth": "",
            "height": "",
            "citizenship": "",
            "club_id": "",
        }
    return {
        "player_id": player.player_id,
        "name": player.name,
        "date_of_birth": player.date_of_birth.strftime("%Y-%m-%d")
        if player.date_of_birth
        else "",
        "height": float(player.height) if player.height else "",
        "citizenship": player.citizenship or "",
        "club_id": player.current_club_id or "",
    }


# --- Games -------------------------------------------------------------------


@app.route("/games")
@login_required
def games():
    season = request.args.get("season", "").strip()
    game_type = request.args.get("type", "").strip()
    league_id = request.args.get("league")
    league_id_int = int(league_id) if league_id else None

    query = Game.query.order_by(Game.game_date.desc())

    if season:
        query = query.filter(Game.season.ilike(f"%{season}%"))
    if game_type:
        query = query.filter(Game.game_type.ilike(f"%{game_type}%"))
    if league_id_int:
        query = query.filter(Game.id_lea == league_id_int)

    games_list = query.limit(50).all()
    attach_participant_names(games_list)
    leagues = League.query.order_by(League.name.asc()).all()
    
    # Get unique seasons and game types for filters
    seasons = db.session.query(Game.season).distinct().order_by(Game.season.desc()).all()
    seasons = [s[0] for s in seasons if s[0]]
    
    game_types = db.session.query(Game.game_type).distinct().order_by(Game.game_type.asc()).all()
    game_types = [t[0] for t in game_types if t[0]]

    return render_template(
        "games.html",
        games=games_list,
        leagues=leagues,
        seasons=seasons,
        game_types=game_types,
        filters={"season": season, "game_type": game_type, "league": league_id},
        active="games",
    )


@app.route("/games/<int:game_id>")
@login_required
def game_detail(game_id):
    game = Game.query.get_or_404(game_id)
    
    # Fetch player stats for this game
    stats = PlayerGameStats.query.filter_by(id_gam=game_id).join(Player).order_by(Player.name).all()
    
    # Calculate total points for each stat entry
    for stat in stats:
        stat.total_points = (stat.points_2pts_made * 2) + (stat.points_3pts_made * 3) + stat.free_throws_made

    return render_template("game_detail.html", game=game, stats=stats)


# --- Admin -------------------------------------------------------------------


@app.route("/admin/sql", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_sql():
    import glob
    
    # Charger les requêtes depuis les fichiers req*.sql et SqlView/*.sql
    queries = {}
    # On cherche les fichiers req*.sql et ceux dans SqlView/
    files = sorted(glob.glob("req*.sql") + glob.glob("SqlView/*.sql"))
    
    for f_path in files:
        # Extraire le nom (ex: "req1" ou "view1")
        key = os.path.splitext(os.path.basename(f_path))[0]
        # Lire le contenu
        try:
            with open(f_path, "r", encoding="utf-8-sig") as f:
                content = f.read().strip()
                queries[key] = content
        except Exception:
            continue

    selected_key = None
    results = None
    columns = None
    error = None
    sql_query = None

    if request.method == "POST":
        selected_key = request.form.get("query_key")
        if selected_key and selected_key in queries:
            sql_query = queries[selected_key]
            try:
                import re
                from sqlalchemy import text
                
                # Détecter si c'est un CREATE VIEW
                view_match = re.search(
                    r'CREATE\s+(?:OR\s+REPLACE\s+)?VIEW\s+(\w+)',
                    sql_query,
                    re.IGNORECASE
                )
                
                if view_match:
                    # C'est une vue : d'abord créer la vue
                    view_name = view_match.group(1)
                    db.session.execute(text(sql_query))
                    db.session.commit()
                    
                    # Puis afficher son contenu
                    select_query = f"SELECT * FROM {view_name}"
                    result_proxy = db.session.execute(text(select_query))
                    columns = result_proxy.keys()
                    results = result_proxy.fetchall()
                    
                    flash(f"Vue '{view_name}' créée/mise à jour avec succès !", "info")
                else:
                    # Requête normale
                    result_proxy = db.session.execute(text(sql_query))
                    if result_proxy.returns_rows:
                        columns = result_proxy.keys()
                        results = result_proxy.fetchall()
                    else:
                        db.session.commit()
            except Exception as e:
                db.session.rollback()
                error = str(e)

    return render_template(
        "sql_runner.html", 
        queries=queries,
        selected_key=selected_key,
        sql_query=sql_query,
        results=results, 
        columns=columns, 
        error=error,
        active="sql"
    )


if __name__ == "__main__":
    app.run(debug=True)
