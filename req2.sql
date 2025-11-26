SELECT
    p.name,
    pgs.free_throws_made,
    pgs.free_throws_attempted,
    ROUND((pgs.free_throws_made::numeric / pgs.free_throws_attempted) * 100, 2) AS free_throw_percentage
FROM player AS p
JOIN player_game_stats AS pgs ON p.id_pla = pgs.id_pla
JOIN game AS g ON pgs.id_gam = g.id_gam
JOIN championship AS c ON g.id_cha = c.id_cha
WHERE
    c.name = 'European Championship'
    AND c.year = 2002
    AND g.game_type = 'Final'
    AND pgs.free_throws_attempted > 0
ORDER BY
    free_throw_percentage DESC,
    pgs.free_throws_attempted DESC
LIMIT 3;
