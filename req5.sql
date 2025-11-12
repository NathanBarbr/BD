WITH current_season AS (
    SELECT MAX(season) AS max_season FROM game WHERE season IS NOT NULL
), player_totals AS (
    SELECT
        p.current_club_id,
        p.id_pla,
        p.name,
        SUM(COALESCE(pgs.points_3pts_made, 0)) AS total_3pts_made
    FROM player AS p
    JOIN player_game_stats AS pgs ON p.id_pla = pgs.id_pla
    JOIN game AS g ON pgs.id_gam = g.id_gam
    WHERE
        p.current_club_id IS NOT NULL
        AND g.season = (SELECT max_season FROM current_season)
        AND EXISTS (
            SELECT 1
            FROM game_participant AS gp
            WHERE gp.id_gam = g.id_gam
              AND gp.participant_type = 'Club'
              AND gp.participant_id = p.current_club_id
        )
    GROUP BY p.current_club_id, p.id_pla, p.name
), ranked_players AS (
    SELECT
        c.name AS club_name,
        pt.name AS player_name,
        pt.total_3pts_made,
        RANK() OVER (PARTITION BY c.id_clu ORDER BY pt.total_3pts_made DESC) AS rnk
    FROM clubs AS c
    JOIN player_totals AS pt ON c.id_clu = pt.current_club_id
)
SELECT
    club_name,
    player_name,
    total_3pts_made
FROM ranked_players
WHERE rnk = 1
ORDER BY club_name;
