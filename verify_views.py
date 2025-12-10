from app import app, db
from sqlalchemy import text

def test_view(view_name):
    print(f"\n--- Testing View: {view_name} ---")
    try:
        # Use text() for raw SQL
        result = db.session.execute(text(f"SELECT * FROM {view_name} LIMIT 5"))
        rows = result.fetchall()
        if not rows:
            print("View created but returned NO rows.")
        else:
            print(f"Success! Retrieved {len(rows)} rows.")
            print("Columns:", result.keys())
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error querying view: {e}")

with app.app_context():
    # Execute View Definitions first
    views = ["view1", "view2", "view3"]
    for v in views:
        try:
            with open(f"SqlView/{v}.sql", "r") as f:
                sql = f.read()
                db.session.execute(text(sql))
                db.session.commit()
                print(f"Executed {v}.sql")
        except Exception as e:
            print(f"Failed to execute {v}.sql: {e}")
            db.session.rollback()

    test_view("top_national_team_scorers")
    test_view("club_average_height")
    test_view("sponsors_of_national_teams")
