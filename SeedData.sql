BEGIN;

TRUNCATE TABLE
    player_game_stats,
    game_participant,
    game,
    member_of,
    participates_in_league,
    participates_in,
    has_sponsor_club,
    has_sponsor_team,
    player,
    clubs,
    national_team,
    sponsor,
    league,
    championship
RESTART IDENTITY CASCADE;

-- Leagues
INSERT INTO league (league_id, name, country, level)
SELECT format('LEA%03s', g),
       format('League %s', g),
       (ARRAY['France','Espagne','Italie','Allemagne','USA'])[1 + (g % 5)],
       (ARRAY['Pro','Elite','Junior','College','Semi-Pro'])[1 + (g % 5)]
FROM generate_series(1, 100) AS g;

-- Championships
INSERT INTO championship (championship_id, name, year, type)
SELECT format('CHA%03s', g),
       format('Championship %s', g),
       2000 + (g % 25),
       (ARRAY['World Cup','Continental','Friendly','Qualifier','Invitational'])[1 + (g % 5)]
FROM generate_series(1, 100) AS g;

-- Clubs
INSERT INTO clubs (club_id, name, city)
SELECT format('CLB%03s', g),
       format('Club %s', g),
       format('City %s', ((g - 1) % 40) + 1)
FROM generate_series(1, 100) AS g;

-- Sponsors
INSERT INTO sponsor (sponsor_id, company_name, city, contact_info)
SELECT format('SPO%03s', g),
       format('Company %s', g),
       format('HQ %s', ((g - 1) % 30) + 1),
       format('contact%s@example.com', g)
FROM generate_series(1, 100) AS g;

-- National teams
INSERT INTO national_team (team_id, country, confederation)
SELECT format('NAT%03s', g),
       format('Country %s', g),
       (ARRAY['FIBA Europe','FIBA Americas','FIBA Africa','FIBA Asia','FIBA Oceania'])[1 + (g % 5)]
FROM generate_series(1, 100) AS g;

-- Players
INSERT INTO player (player_id, name, date_of_birth, height, citizenship, current_club_id)
SELECT format('PLY%04s', g),
       format('Player %s', g),
       DATE '1980-01-01' + ((g - 1) % 1000),
       1.75 + ((g % 25) * 0.01),
       format('Nation %s', ((g - 1) % 60) + 1),
       ((g - 1) % 100) + 1
FROM generate_series(1, 300) AS g;

-- League participation (each club linked to two leagues)
INSERT INTO participates_in_league (id_lea, id_clu)
SELECT ((g - 1) % 100) + 1, g
FROM generate_series(1, 100) AS g
UNION ALL
SELECT ((g + 24) % 100) + 1, g
FROM generate_series(1, 100) AS g;

-- Championship participation (national teams)
INSERT INTO participates_in (id_cha, id_nat)
SELECT ((g - 1) % 100) + 1, g
FROM generate_series(1, 100) AS g
UNION ALL
SELECT ((g + 33) % 100) + 1, g
FROM generate_series(1, 100) AS g;

-- Club sponsors
INSERT INTO has_sponsor_club (id_clu, id_spo)
SELECT g, ((g - 1) % 100) + 1
FROM generate_series(1, 100) AS g
UNION ALL
SELECT g, ((g + 9) % 100) + 1
FROM generate_series(1, 100) AS g;

-- National team sponsors
INSERT INTO has_sponsor_team (id_nat, id_spo)
SELECT g, ((g + 19) % 100) + 1
FROM generate_series(1, 100) AS g
UNION ALL
SELECT g, ((g + 49) % 100) + 1
FROM generate_series(1, 100) AS g;

-- National memberships for players
INSERT INTO member_of (id_pla, id_nat, date_start, date_end)
SELECT g,
       ((g - 1) % 100) + 1,
       DATE '2010-01-01' + ((g - 1) % 200),
       NULL
FROM generate_series(1, 300) AS g;

-- Games (mix league and championship)
INSERT INTO game (game_id, game_date, location, game_type, season, id_lea, id_cha)
SELECT format('G%04s', g),
       CURRENT_DATE - ((g - 1) % 365),
       format('Arena %s', ((g - 1) % 50) + 1),
       (ARRAY['Regular','Playoff','Final','Friendly','Qualifier'])[1 + (g % 5)],
       format('%s/%s', 2018 + (g % 5), 2019 + (g % 5)),
       CASE WHEN g % 2 = 0 THEN ((g - 1) % 100) + 1 ELSE NULL END,
       CASE WHEN g % 2 = 1 THEN ((g - 1) % 100) + 1 ELSE NULL END
FROM generate_series(1, 150) AS g;

-- Game participants for league games (clubs)
WITH ordered_games AS (
    SELECT id_gam,
           ROW_NUMBER() OVER (ORDER BY id_gam) AS rn
    FROM game
    WHERE id_lea IS NOT NULL
)
INSERT INTO game_participant (id_gam, participant_id, participant_type, score, role)
SELECT og.id_gam,
       ((og.rn + shift) % 100) + 1,
       'Club',
       70 + ((og.rn + shift * 7) % 35),
       CASE WHEN shift = 0 THEN 'Home' ELSE 'Away' END
FROM ordered_games AS og
CROSS JOIN (VALUES (0), (13)) AS s(shift);

-- Game participants for championship games (national teams)
WITH ordered_games AS (
    SELECT id_gam,
           ROW_NUMBER() OVER (ORDER BY id_gam) AS rn
    FROM game
    WHERE id_cha IS NOT NULL
)
INSERT INTO game_participant (id_gam, participant_id, participant_type, score, role)
SELECT og.id_gam,
       ((og.rn + shift) % 100) + 1,
       'National',
       65 + ((og.rn + shift * 5) % 30),
       CASE WHEN shift = 0 THEN 'Home' ELSE 'Away' END
FROM ordered_games AS og
CROSS JOIN (VALUES (0), (21)) AS s(shift);

-- Player stats (500 uniques)
WITH limited_pairs AS (
    SELECT g.id_gam, p.id_pla
    FROM game AS g
    CROSS JOIN player AS p
    ORDER BY g.id_gam, p.id_pla
    LIMIT 500
),
ranked_pairs AS (
    SELECT lp.id_gam,
           lp.id_pla,
           ROW_NUMBER() OVER (ORDER BY lp.id_gam, lp.id_pla) AS seq
    FROM limited_pairs AS lp
)
INSERT INTO player_game_stats (
    id_gam,
    id_pla,
    id_stat,
    points_2pts_made,
    points_2pts_attempted,
    points_3pts_made,
    points_3pts_attempted,
    free_throws_made,
    free_throws_attempted,
    assists,
    rebounds,
    blocks
)
SELECT rp.id_gam,
       rp.id_pla,
       rp.seq,
       (rp.seq % 10) + 2,
       (rp.seq % 10) + 5,
       (rp.seq % 5),
       (rp.seq % 5) + 3,
       (rp.seq % 6),
       (rp.seq % 6) + 2,
       (rp.seq % 8),
       (rp.seq % 12),
       (rp.seq % 3)
FROM ranked_pairs AS rp;

COMMIT;


