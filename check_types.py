from app import app, db, Game

with app.app_context():
    types = db.session.query(Game.game_type).distinct().all()
    print("Game Types:", [t[0] for t in types])
