SELECT
    p.name,
    pgs.free_throws_made AS free_throws
FROM player AS p
JOIN player_game_stats AS pgs ON p.id_pla = pgs.id_pla
JOIN game AS g ON pgs.id_gam = g.id_gam
JOIN championship AS c ON g.id_cha = c.id_cha
WHERE
    c.name = 'European Championship'
    AND c.year = 2002
    AND g.game_type = 'Final'
ORDER BY pgs.free_throws_made DESC
LIMIT 3;
