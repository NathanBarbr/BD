from app import app, db, Player, NationalTeam, Club
from sqlalchemy import func

with app.app_context():
    print("--- Player Citizenship Distribution ---")
    citizenship_data = db.session.query(Player.citizenship, func.count(Player.id_pla)).group_by(Player.citizenship).all()
    total_players = 0
    for c, count in citizenship_data:
        print(f"'{c}': {count}")
        total_players += count
    print(f"Total Players in DB: {Player.query.count()}")
    print(f"Sum of grouped counts: {total_players}")

    print("\n--- National Team Confederations ---")
    confederations = db.session.query(NationalTeam.confederation).distinct().all()
    print("Unique Confederations:", [c[0] for c in confederations])
    
    print("\n--- National Team Data Sample ---")
    teams = NationalTeam.query.limit(10).all()
    for t in teams:
        print(f"{t.country}: {t.confederation}")

    print("\n--- Players with NULL Citizenship ---")
    null_citizenship = Player.query.filter(Player.citizenship == None).count()
    print(f"Count: {null_citizenship}")
