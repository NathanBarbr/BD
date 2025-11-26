import os
import random
from datetime import date, timedelta

import psycopg2
from faker import Faker

# Initialize Faker
fake = Faker(['en_US', 'fr_FR', 'es_ES', 'it_IT'])

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "basketball"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "secret"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )

def run_seed():
    conn = get_connection()
    cur = conn.cursor()

    print("Cleaning database...")
    cur.execute("""
        TRUNCATE TABLE
            player_game_stats, game_participant, game, member_of,
            participates_in_league, participates_in, has_sponsor_club,
            has_sponsor_team, player, clubs, national_team, sponsor,
            league, championship
        RESTART IDENTITY CASCADE;
    """)

    print("Inserting Curated Data (Required for Exercises)...")
    # --- Curated Data (Must match SeedData.sql logic for exercises) ---

    # 1. Leagues
    cur.execute("INSERT INTO league (league_id, name, country, level) VALUES (%s, %s, %s, %s) RETURNING id_lea",
                ('LEA_EURL', 'Euroleague', 'Europe', 'Elite'))
    id_lea_euro = cur.fetchone()[0]

    # 2. Clubs
    curated_clubs = [
        ('CLB_BAR', 'FC Barcelona', 'Barcelona'),
        ('CLB_RMA', 'Real Madrid', 'Madrid'),
        ('CLB_ASV', 'ASVEL Lyon-Villeurbanne', 'Lyon'),
        ('CLB_MTA', 'Maccabi Tel Aviv', 'Tel Aviv'),
        ('CLB_CSK', 'CSKA Moscow', 'Moscow'),
        ('CLB_PAN', 'Panathinaikos', 'Athens')
    ]
    club_map = {} # club_id_str -> db_id
    for cid, name, city in curated_clubs:
        cur.execute("INSERT INTO clubs (club_id, name, city) VALUES (%s, %s, %s) RETURNING id_clu", (cid, name, city))
        club_map[cid] = cur.fetchone()[0]

    # 3. National Teams
    curated_teams = [
        ('NAT_ESP', 'Spain', 'FIBA Europe'),
        ('NAT_LTU', 'Lithuania', 'FIBA Europe'),
        ('NAT_FRA', 'France', 'FIBA Europe'),
        ('NAT_ARG', 'Argentina', 'FIBA Americas'),
        ('NAT_USA', 'United States', 'FIBA Americas')
    ]
    team_map = {} # team_id_str -> db_id
    for tid, country, conf in curated_teams:
        cur.execute("INSERT INTO national_team (team_id, country, confederation) VALUES (%s, %s, %s) RETURNING id_nat", (tid, country, conf))
        team_map[tid] = cur.fetchone()[0]

    # 4. Sponsors
    curated_sponsors = [
        ('SPO_NIKE', 'Nike', 'Beaverton', 'nike@example.com'),
        ('SPO_ADID', 'Adidas', 'Herzogenaurach', 'adidas@example.com'),
        ('SPO_PEAK', 'Peak', 'Beijing', 'peak@example.com')
    ]
    sponsor_map = {}
    for sid, name, city, contact in curated_sponsors:
        cur.execute("INSERT INTO sponsor (sponsor_id, company_name, city, contact_info) VALUES (%s, %s, %s, %s) RETURNING id_spo", (sid, name, city, contact))
        sponsor_map[sid] = cur.fetchone()[0]

    # 5. Championships
    curated_champs = [
        ('CHA_EC2002', 'European Championship', 2002, 'Continental'),
        ('CHA_WC2019', 'World Championship', 2019, 'World Cup'),
        ('CHA_WC2023', 'World Championship', 2023, 'World Cup')
    ]
    champ_map = {}
    for cid, name, year, ctype in curated_champs:
        cur.execute("INSERT INTO championship (championship_id, name, year, type) VALUES (%s, %s, %s, %s) RETURNING id_cha", (cid, name, year, ctype))
        champ_map[cid] = cur.fetchone()[0]

    # 6. Players
    curated_players = [
        ('PLY_GASOL', 'Pau Gasol', '1980-07-06', 2.16, 'Spain', 'CLB_BAR'),
        ('PLY_NAVRO', 'Juan Carlos Navarro', '1980-06-13', 1.96, 'Spain', 'CLB_BAR'),
        ('PLY_RUBIO', 'Ricky Rubio', '1990-10-21', 1.93, 'Spain', 'CLB_BAR'),
        ('PLY_MIROTC', 'Nikola Mirotic', '1991-02-11', 2.08, 'Montenegro', 'CLB_BAR'),
        ('PLY_JASI', 'Sarunas Jasikevicius', '1976-03-05', 1.93, 'Lithuania', 'CLB_MTA'),
        ('PLY_MACI', 'Arvydas Macijauskas', '1980-01-19', 1.95, 'Lithuania', 'CLB_PAN'),
        ('PLY_PARKER', 'Tony Parker', '1982-05-17', 1.88, 'France', 'CLB_ASV'),
        ('PLY_DIAW', 'Boris Diaw', '1982-04-16', 2.03, 'France', 'CLB_ASV'),
        ('PLY_BATUM', 'Nicolas Batum', '1988-12-14', 2.03, 'France', 'CLB_ASV'),
        ('PLY_SCOLA', 'Luis Scola', '1980-04-30', 2.06, 'Argentina', 'CLB_RMA'),
        ('PLY_GINOBI', 'Manu Ginobili', '1977-07-28', 1.98, 'Argentina', 'CLB_RMA'),
        ('PLY_CAMPA', 'Facundo Campazzo', '1991-03-23', 1.81, 'Argentina', 'CLB_RMA'),
        ('PLY_DURANT', 'Kevin Durant', '1988-09-29', 2.10, 'United States', 'CLB_CSK'),
        ('PLY_CURRY', 'Stephen Curry', '1988-03-14', 1.91, 'United States', 'CLB_CSK')
    ]
    player_map = {}
    for pid, name, dob, h, cit, cid in curated_players:
        cur.execute("""
            INSERT INTO player (player_id, name, date_of_birth, height, citizenship, current_club_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_pla
        """, (pid, name, dob, h, cit, club_map[cid]))
        player_map[pid] = cur.fetchone()[0]

    # 7. Relationships (Curated)
    # Euroleague participation
    for cid in club_map.values():
        cur.execute("INSERT INTO participates_in_league (id_lea, id_clu) VALUES (%s, %s)", (id_lea_euro, cid))

    # National Team Participation
    nt_parts = [
        ('CHA_EC2002', 'NAT_ESP'), ('CHA_EC2002', 'NAT_LTU'),
        ('CHA_WC2019', 'NAT_ESP'), ('CHA_WC2019', 'NAT_ARG'),
        ('CHA_WC2023', 'NAT_USA'), ('CHA_WC2023', 'NAT_FRA')
    ]
    for ch_id, tm_id in nt_parts:
        cur.execute("INSERT INTO participates_in (id_cha, id_nat) VALUES (%s, %s)", (champ_map[ch_id], team_map[tm_id]))

    # Sponsors
    tm_sponsors = [
        ('NAT_ESP', 'SPO_NIKE'), ('NAT_USA', 'SPO_NIKE'),
        ('NAT_ARG', 'SPO_PEAK'), ('NAT_FRA', 'SPO_ADID'), ('NAT_LTU', 'SPO_ADID')
    ]
    for tm_id, sp_id in tm_sponsors:
        cur.execute("INSERT INTO has_sponsor_team (id_nat, id_spo) VALUES (%s, %s)", (team_map[tm_id], sponsor_map[sp_id]))

    # Member Of
    mem_of = [
        ('PLY_GASOL', 'NAT_ESP'), ('PLY_NAVRO', 'NAT_ESP'), ('PLY_RUBIO', 'NAT_ESP'),
        ('PLY_JASI', 'NAT_LTU'), ('PLY_MACI', 'NAT_LTU'),
        ('PLY_PARKER', 'NAT_FRA'), ('PLY_DIAW', 'NAT_FRA'), ('PLY_BATUM', 'NAT_FRA'),
        ('PLY_SCOLA', 'NAT_ARG'), ('PLY_GINOBI', 'NAT_ARG'), ('PLY_CAMPA', 'NAT_ARG'),
        ('PLY_DURANT', 'NAT_USA'), ('PLY_CURRY', 'NAT_USA')
    ]
    for pid, tm_id in mem_of:
        cur.execute("INSERT INTO member_of (id_pla, id_nat, date_start) VALUES (%s, %s, '2000-01-01')", (player_map[pid], team_map[tm_id]))

    # 8. Games & Stats (Curated)
    # Helper to insert game and participants
    def insert_game(gid, date, loc, gtype, season, lea, cha, participants):
        cur.execute("""
            INSERT INTO game (game_id, game_date, location, game_type, season, id_lea, id_cha)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_gam
        """, (gid, date, loc, gtype, season, lea, cha))
        id_gam = cur.fetchone()[0]
        for pid, ptype, score, role in participants:
            real_pid = club_map[pid] if ptype == 'Club' else team_map[pid]
            cur.execute("""
                INSERT INTO game_participant (id_gam, participant_id, participant_type, score, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_gam, real_pid, ptype, score, role))
        return id_gam

    # Championship Finals
    g_ec02 = insert_game('EC02FINAL', '2002-09-08', 'Berlin Arena', 'Final', '2001/2002', None, champ_map['CHA_EC2002'],
                         [('NAT_ESP', 'National', 85, 'Home'), ('NAT_LTU', 'National', 78, 'Away')])
    g_wc19 = insert_game('WC19FINAL', '2019-09-15', 'Beijing National Indoor', 'Final', '2018/2019', None, champ_map['CHA_WC2019'],
                         [('NAT_ESP', 'National', 95, 'Home'), ('NAT_ARG', 'National', 75, 'Away')])
    g_wc23 = insert_game('WC23FINAL', '2023-09-10', 'Manila Arena', 'Final', '2022/2023', None, champ_map['CHA_WC2023'],
                         [('NAT_USA', 'National', 101, 'Home'), ('NAT_FRA', 'National', 97, 'Away')])

    # Euroleague Finals
    insert_game('EU18FINAL', '2018-05-20', 'Belgrade Arena', 'Final', '2017/2018', id_lea_euro, None,
                [('CLB_BAR', 'Club', 92, 'Home'), ('CLB_RMA', 'Club', 86, 'Away')])
    insert_game('EU19FINAL', '2019-05-19', 'Vitoria-Gasteiz Arena', 'Final', '2018/2019', id_lea_euro, None,
                [('CLB_BAR', 'Club', 85, 'Home'), ('CLB_CSK', 'Club', 79, 'Away')])
    insert_game('EU20FINAL', '2020-05-24', 'Cologne Arena', 'Final', '2019/2020', id_lea_euro, None,
                [('CLB_BAR', 'Club', 87, 'Home'), ('CLB_PAN', 'Club', 80, 'Away')])
    insert_game('EU21FINAL', '2021-05-30', 'Kaunas Arena', 'Final', '2020/2021', id_lea_euro, None,
                [('CLB_BAR', 'Club', 89, 'Home'), ('CLB_MTA', 'Club', 83, 'Away')])

    # Euroleague Regular Season 24/25
    g_eu25_1 = insert_game('EU25BRRM', '2024-10-14', 'Palau Blaugrana', 'Regular', '2024/2025', id_lea_euro, None,
                           [('CLB_BAR', 'Club', 98, 'Home'), ('CLB_RMA', 'Club', 90, 'Away')])
    g_eu25_2 = insert_game('EU25ASMT', '2024-11-02', 'Astroballe', 'Regular', '2024/2025', id_lea_euro, None,
                           [('CLB_ASV', 'Club', 88, 'Home'), ('CLB_MTA', 'Club', 84, 'Away')])
    g_eu25_3 = insert_game('EU25BRMT', '2025-01-12', 'Palau Blaugrana', 'Regular', '2024/2025', id_lea_euro, None,
                           [('CLB_BAR', 'Club', 91, 'Home'), ('CLB_MTA', 'Club', 88, 'Away')])

    # Player Stats (Curated)
    stats_data = [
        (g_ec02, 'PLY_GASOL', 11, 16, 3, 5, 11, 13, 4, 12, 3),
        (g_ec02, 'PLY_NAVRO', 9, 14, 4, 7, 10, 10, 7, 5, 1),
        (g_ec02, 'PLY_JASI', 8, 13, 5, 9, 8, 9, 9, 4, 0),
        (g_ec02, 'PLY_MACI', 7, 12, 5, 10, 8, 10, 6, 3, 0),
        (g_wc19, 'PLY_GASOL', 9, 13, 2, 5, 10, 11, 5, 11, 2),
        (g_wc19, 'PLY_RUBIO', 6, 10, 3, 7, 11, 12, 11, 7, 1),
        (g_wc19, 'PLY_SCOLA', 7, 12, 1, 4, 8, 9, 3, 9, 1),
        (g_wc19, 'PLY_GINOBI', 6, 11, 2, 6, 5, 6, 4, 5, 1),
        (g_wc19, 'PLY_CAMPA', 5, 9, 4, 8, 6, 7, 9, 4, 0),
        (g_wc23, 'PLY_PARKER', 11, 16, 4, 6, 11, 12, 12, 6, 0),
        (g_wc23, 'PLY_DURANT', 12, 18, 4, 8, 10, 11, 5, 8, 2),
        (g_eu25_1, 'PLY_GASOL', 8, 13, 1, 3, 4, 5, 5, 10, 2),
        (g_eu25_1, 'PLY_NAVRO', 6, 11, 5, 8, 6, 6, 9, 4, 0),
        (g_eu25_1, 'PLY_RUBIO', 5, 9, 3, 5, 7, 8, 11, 5, 1),
        (g_eu25_1, 'PLY_CAMPA', 4, 8, 4, 7, 5, 5, 10, 3, 0),
        (g_eu25_1, 'PLY_GINOBI', 5, 9, 2, 6, 4, 4, 4, 4, 1),
        (g_eu25_1, 'PLY_SCOLA', 7, 12, 1, 4, 3, 4, 3, 9, 1),
        (g_eu25_3, 'PLY_GASOL', 7, 12, 2, 4, 6, 7, 6, 11, 2),
        (g_eu25_3, 'PLY_NAVRO', 5, 9, 6, 9, 5, 5, 8, 3, 0),
        (g_eu25_3, 'PLY_RUBIO', 4, 8, 4, 7, 6, 7, 12, 6, 1),
        (g_eu25_3, 'PLY_JASI', 6, 10, 7, 10, 4, 5, 7, 2, 0),
        (g_eu25_3, 'PLY_MACI', 5, 9, 5, 11, 6, 7, 5, 3, 0),
        (g_eu25_2, 'PLY_PARKER', 8, 12, 5, 7, 7, 8, 13, 3, 0),
        (g_eu25_2, 'PLY_DIAW', 6, 10, 3, 9, 4, 5, 7, 7, 1),
        (g_eu25_2, 'PLY_BATUM', 5, 9, 4, 9, 5, 6, 6, 6, 1),
        (g_eu25_2, 'PLY_JASI', 5, 9, 6, 9, 5, 6, 8, 4, 0),
        (g_eu25_2, 'PLY_MACI', 6, 11, 4, 10, 4, 5, 4, 5, 0)
    ]
    for gid, pid, p2m, p2a, p3m, p3a, ftm, fta, ast, reb, blk in stats_data:
        cur.execute("""
            INSERT INTO player_game_stats (id_gam, id_pla, points_2pts_made, points_2pts_attempted,
            points_3pts_made, points_3pts_attempted, free_throws_made, free_throws_attempted,
            assists, rebounds, blocks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (gid, player_map[pid], p2m, p2a, p3m, p3a, ftm, fta, ast, reb, blk))

    print("Inserting Realistic Filler Data...")
    # --- Filler Data (Realistic names via Faker) ---

    # 1. Leagues (20)
    filler_leagues = []
    for _ in range(20):
        name = f"{fake.country()} {random.choice(['League', 'Pro A', 'Elite', 'Basket League', 'Premier League'])}"
        cur.execute("INSERT INTO league (league_id, name, country, level) VALUES (%s, %s, %s, %s) RETURNING id_lea",
                    (fake.unique.bothify(text='LEA###'), name, fake.country(), random.choice(['Pro', 'Elite', 'D1'])))
        filler_leagues.append(cur.fetchone()[0])

    # 2. Clubs (50)
    filler_clubs = []
    for _ in range(50):
        city = fake.city()
        name = f"{city} {random.choice(['Basket', 'Lions', 'Tigers', 'Hoops', 'BC', 'United'])}"
        cur.execute("INSERT INTO clubs (club_id, name, city) VALUES (%s, %s, %s) RETURNING id_clu",
                    (fake.unique.bothify(text='CLB###'), name, city))
        cid = cur.fetchone()[0]
        filler_clubs.append(cid)
        # Link to a random league
        cur.execute("INSERT INTO participates_in_league (id_lea, id_clu) VALUES (%s, %s)",
                    (random.choice(filler_leagues), cid))

    # 3. Players (200)
    filler_players = []
    for _ in range(200):
        dob = fake.date_of_birth(minimum_age=18, maximum_age=38)
        cur.execute("""
            INSERT INTO player (player_id, name, date_of_birth, height, citizenship, current_club_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id_pla
        """, (fake.unique.bothify(text='PLY####'), fake.name_male(), dob,
              round(random.uniform(1.80, 2.20), 2), fake.country(), random.choice(filler_clubs)))
        filler_players.append(cur.fetchone()[0])

    # 4. Games (100 random games)
    for _ in range(100):
        is_league = random.choice([True, False])
        if is_league:
            lid = random.choice(filler_leagues)
            cid = None
            gtype = 'Regular'
        else:
            lid = None
            cid = champ_map['CHA_WC2023'] # Reuse a champ for simplicity or create new ones
            gtype = 'Group Stage'

        cur.execute("""
            INSERT INTO game (game_id, game_date, location, game_type, season, id_lea, id_cha)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id_gam
        """, (fake.unique.bothify(text='GAM####'), fake.date_between(start_date='-1y', end_date='today'),
              fake.city(), gtype, '2023/2024', lid, cid))
        gid = cur.fetchone()[0]

        # Participants (Just pick 2 random clubs for simplicity, even if champ game for filler)
        c1, c2 = random.sample(filler_clubs, 2)
        s1, s2 = random.randint(60, 110), random.randint(60, 110)
        cur.execute("INSERT INTO game_participant (id_gam, participant_id, participant_type, score, role) VALUES (%s, %s, 'Club', %s, 'Home')", (gid, c1, s1))
        cur.execute("INSERT INTO game_participant (id_gam, participant_id, participant_type, score, role) VALUES (%s, %s, 'Club', %s, 'Away')", (gid, c2, s2))

        # Stats for some players in these clubs
        # (Simplified: just pick random players from the DB to give them stats)
        for pid in random.sample(filler_players, 5):
            cur.execute("""
                INSERT INTO player_game_stats (id_gam, id_pla, points_2pts_made, points_2pts_attempted,
                points_3pts_made, points_3pts_attempted, free_throws_made, free_throws_attempted,
                assists, rebounds, blocks)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (gid, pid, random.randint(0, 10), random.randint(5, 15),
                  random.randint(0, 5), random.randint(0, 10),
                  random.randint(0, 5), random.randint(0, 10),
                  random.randint(0, 10), random.randint(0, 15), random.randint(0, 3)))

    conn.commit()
    cur.close()
    conn.close()
    print("Database seeded successfully with Realistic & Curated data!")

if __name__ == "__main__":
    run_seed()
