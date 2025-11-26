WITH current_season AS (
    SELECT MAX(season) AS max_season
    FROM game
    WHERE season IS NOT NULL
), player_totals AS (
    SELECT
        p.current_club_id,
        p.id_pla,
        p.name,
        SUM(COALESCE(pgs.points_3pts_made, 0)) AS total_3pts_made,
        SUM(COALESCE(pgs.points_3pts_attempted, 0)) AS total_3pts_attempted
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
), player_percentages AS (
    SELECT
        current_club_id,
        id_pla,
        name,
        total_3pts_made,
        total_3pts_attempted,
        CASE
            WHEN total_3pts_attempted > 0 THEN total_3pts_made::numeric / total_3pts_attempted
            ELSE NULL
        END AS three_pt_percentage
    FROM player_totals
), ranked_players AS (
    SELECT
        c.name AS club_name,
        pp.name AS player_name,
        pp.three_pt_percentage,
        RANK() OVER (PARTITION BY c.id_clu ORDER BY pp.three_pt_percentage DESC NULLS LAST) AS rnk
    FROM clubs AS c
    JOIN player_percentages AS pp ON c.id_clu = pp.current_club_id
)
SELECT
    club_name,
    player_name,
    ROUND(three_pt_percentage * 100, 2) AS three_pt_percentage
FROM ranked_players
WHERE rnk = 1
  AND three_pt_percentage IS NOT NULL
ORDER BY club_name;
