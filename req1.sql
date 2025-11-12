SELECT
    p.name,
    SUM(
        COALESCE(pgs.points_2pts_made, 0) * 2
        + COALESCE(pgs.points_3pts_made, 0) * 3
        + COALESCE(pgs.free_throws_made, 0)
    ) AS total_national_points
FROM player AS p
JOIN player_game_stats AS pgs ON p.id_pla = pgs.id_pla
JOIN game AS g ON pgs.id_gam = g.id_gam
WHERE g.id_cha IS NOT NULL
GROUP BY p.id_pla, p.name
ORDER BY total_national_points DESC
LIMIT 10;
